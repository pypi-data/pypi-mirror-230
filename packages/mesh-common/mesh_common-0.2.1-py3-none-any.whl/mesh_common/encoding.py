import struct
import time
import zlib
from typing import (
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Iterable,
    NamedTuple,
    Optional,
    Type,
    Union,
)

from urllib3.response import GzipDecoderState

from mesh_common import to_async_iterator


class ContentEncodingNegotiation(NamedTuple):
    """
    result of the content encoding negotiation
    encoders / decoders are the sequence of encodings / decodings required to apply to the content to match the
    accept_encoding e.g. if content_encoding=gzip,deflate,gzip  accept_encoding=gzip
    would result in decoders['gzip', 'deflate'] ( decode gzip and deflate but leave the first gzip )
    """

    accept_encoding: str
    original_encoding: str
    negotiated_encoding: str

    decoders: list[str]
    encoders: list[str]

    @property
    def changed(self) -> bool:
        return self.original_encoding != self.negotiated_encoding

    @property
    def unchanged(self) -> bool:
        return self.original_encoding == self.negotiated_encoding


def negotiate_encoding(
    content_encoding: Optional[str], accept_encoding: Optional[str], auto_gzip=False
) -> ContentEncodingNegotiation:
    """
    compare the current content encoding with the accepts header and negotiate the content encoding
    and the sequence of decode / encode actions to apply
    https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-encoding
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding
    """

    content_encoding = (content_encoding or "").strip().lower()
    accept_encoding = (accept_encoding or "").strip().lower()

    content_encodings = [
        enc.strip().split(";")[0] for enc in (content_encoding or "").strip().lower().split(",") if enc.strip()
    ]
    content_encoding = ",".join(content_encodings).strip()
    accept_encodings = {enc.strip().strip(";").split(";")[0] for enc in accept_encoding.split(",") if enc.strip()}
    accept_encodings = {key for key in accept_encodings if key and not key == "*"}
    encodings = set(content_encodings)
    unaccepted_encodings = encodings - accept_encodings

    decoders: list[str] = []
    encoders: list[str] = []

    while unaccepted_encodings:
        decoders.append(content_encodings.pop(-1))
        unaccepted_encodings = set(content_encodings) - accept_encodings

    encodings = set(content_encodings)

    if not encodings and auto_gzip and "gzip" in accept_encodings:
        encoders.append("gzip")
        content_encodings.append("gzip")

    return ContentEncodingNegotiation(
        original_encoding=content_encoding,
        accept_encoding=accept_encoding,
        negotiated_encoding=",".join(content_encodings),
        decoders=decoders,
        encoders=encoders,
    )


def _gzip_header(compress_level: int, filename: Optional[str] = None, mtime: Optional[float] = None) -> bytes:
    """
    translated from stdlib GzipFile to support async streaming
    https://github.com/python/cpython/blob/3faa9f78d4b9a8c0fd4657b434bdb08ae1f28800/Lib/gzip.py#L240
    """
    header_parts = [
        b"\037\213",  # magic header
        b"\010",  # compression method
    ]

    try:
        name_bytes = (filename or "").strip().encode("latin-1")
        if name_bytes.endswith(b".gz"):
            name_bytes = name_bytes[:-3]
    except UnicodeEncodeError:
        name_bytes = b""

    header_parts.append(b"\x08" if filename else b"\x00")

    if mtime is None:
        mtime = time.time()

    # pack as little endian long
    # https://github.com/python/cpython/blob/3faa9f78d4b9a8c0fd4657b434bdb08ae1f28800/Lib/gzip.py#L70
    header_parts.append(struct.pack("<L", int(mtime)))

    if compress_level == zlib.Z_BEST_COMPRESSION:
        xfl = b"\002"
    elif compress_level == zlib.Z_BEST_SPEED:
        xfl = b"\004"
    else:
        xfl = b"\000"

    header_parts.append(xfl)
    header_parts.append(b"\377")
    if filename:
        header_parts.append(name_bytes)
        header_parts.append(b"\000")

    return b"".join(header_parts)


class _StreamWrapper(AsyncIterable[bytes]):
    def __init__(self, raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes]):
        self._iterator = self._wrap_stream(raw_stream)

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        return await self._iterator.__anext__()

    @staticmethod
    def _wrap_stream(raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes]) -> AsyncIterator[bytes]:

        if isinstance(raw_stream, AsyncIterable):
            return raw_stream.__aiter__()  # pylint: disable=unnecessary-dunder-call

        if isinstance(raw_stream, (bytes, bytearray)):
            chunk: bytes = raw_stream

            async def _iter() -> AsyncGenerator[bytes, None]:
                yield chunk

            return _iter()

        return to_async_iterator(raw_stream.__iter__())  # pylint: disable=unnecessary-dunder-call


class _GZipStreamEncoder(_StreamWrapper):
    def __init__(
        self,
        raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes],
        compress_level: int = zlib.Z_BEST_COMPRESSION,
    ):
        super().__init__(raw_stream)
        self._zlib = zlib.compressobj(compress_level, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
        self._header = _gzip_header(compress_level)
        self._header_sent = False
        self._finished = False
        self._crc = zlib.crc32(b"")
        self._size = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._finished:
            raise StopAsyncIteration()
        buffer = b""
        if not self._header_sent:
            self._header_sent = True
            buffer = self._header

        compressed = b""
        try:
            while not compressed:
                chunk = await super().__anext__()
                if not chunk:
                    continue
                self._size += len(chunk)
                self._crc = zlib.crc32(chunk, self._crc)
                compressed = self._zlib.compress(chunk)

        except StopAsyncIteration:
            self._finished = True
            # https://github.com/python/cpython/blob/3faa9f78d4b9a8c0fd4657b434bdb08ae1f28800/Lib/gzip.py#L334
            flushed = self._zlib.flush(zlib.Z_FINISH)
            flushed = flushed + struct.pack("<L", self._crc) + struct.pack("<L", self._size & 0xFFFFFFFF)
            compressed = compressed + flushed

        return buffer + compressed if buffer else compressed


class _DeflateStreamDecoder(_StreamWrapper):
    """
    derived from urllib3.response.DeflateDecoder
    https://github.com/urllib3/urllib3/blob/main/src/urllib3/response.py#L63
    """

    def __init__(self, raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes]):
        super().__init__(raw_stream)
        self._zlib = zlib.decompressobj()
        self._first_try = True

    def __aiter__(self):
        return self

    async def __anext__(self):

        buffer = b""
        decompressed = b""
        zlib_err: Optional[Exception] = None
        try:
            while not decompressed:
                chunk = await super().__anext__()
                if not chunk:
                    continue

                buffer = buffer + chunk if self._first_try else chunk
                try:
                    decompressed = self._zlib.decompress(chunk)
                    if decompressed:
                        self._first_try = False
                        buffer = b""
                except zlib.error as ex:
                    if not self._first_try:
                        raise
                    self._first_try = False
                    self._zlib = zlib.decompressobj(-zlib.MAX_WBITS)
                    try:
                        decompressed = self._zlib.decompress(buffer)
                    finally:
                        buffer = b""
                    zlib_err = ex

                    continue

        except StopAsyncIteration:
            if buffer:
                if zlib_err:
                    raise zlib.error from zlib_err
                raise zlib.error  # pylint: disable=raise-missing-from
            raise

        return decompressed


class _GZipStreamDecoder(_StreamWrapper):
    """
    derived from urllib3.response.GzipDecoder
    https://github.com/urllib3/urllib3/blob/main/src/urllib3/response.py#L102
    """

    def __init__(self, raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes]):
        super().__init__(raw_stream)
        self._zlib = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self._state: int = GzipDecoderState.FIRST_MEMBER
        self._finished = False

    def __aiter__(self):
        return self

    async def __anext__(self):

        if self._finished:
            raise StopAsyncIteration()

        while True:
            chunk = await super().__anext__()
            if not chunk or self._state == GzipDecoderState.SWALLOW_DATA:
                continue

            decompressed = b""
            while chunk:
                try:
                    decompressed += self._zlib.decompress(chunk)
                except zlib.error:
                    previous_state = self._state
                    self._state = GzipDecoderState.SWALLOW_DATA
                    if previous_state == GzipDecoderState.OTHER_MEMBERS:
                        continue
                    raise
                chunk = self._zlib.unused_data
                if not chunk:
                    return decompressed
                self._state = GzipDecoderState.OTHER_MEMBERS
                self._zlib = zlib.decompressobj(16 + zlib.MAX_WBITS)


_ENCODERS: dict[str, Type[_StreamWrapper]] = {"gzip": _GZipStreamEncoder}
_DECODERS: dict[str, Type[_StreamWrapper]] = {"gzip": _GZipStreamDecoder, "deflate": _DeflateStreamDecoder}


async def negotiated_stream(
    negotiation: ContentEncodingNegotiation, raw_stream: Union[AsyncIterable[bytes], Iterable[bytes], bytes]
) -> AsyncIterable[bytes]:
    """
    use the result of the content encoding negotiation to wrap the underlying stream to support stream
    encoding or decoding as required
    """
    # list of content decoders to apply in sequence
    decoders = negotiation.decoders
    # list of content encoders to apply in sequence
    encoders = negotiation.encoders

    stream = _StreamWrapper(raw_stream)
    for decoding in decoders:
        stream = _DECODERS[decoding](stream)

    for encoding in encoders:
        stream = _ENCODERS[encoding](stream)

    async for chunk in stream:
        yield chunk
