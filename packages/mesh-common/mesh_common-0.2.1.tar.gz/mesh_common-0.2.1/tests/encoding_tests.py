import gzip
import math
import os
import zlib
from typing import AsyncIterable, Callable, cast
from uuid import uuid4

import pytest
from nhs_aws_helpers import async_stream_from_s3

from mesh_common.constants import KiB
from mesh_common.encoding import (
    ContentEncodingNegotiation,
    _StreamWrapper,
    negotiate_encoding,
    negotiated_stream,
)


@pytest.mark.parametrize(
    "content_encoding, accept_encoding, auto_gzip, expected_encoding, expected_encoders, expected_decoders",
    [
        ("", "", True, "", [], []),
        ("", "", False, "", [], []),
        ("", "*", True, "", [], []),
        ("", "*", False, "", [], []),
        ("", "gzip", True, "gzip", ["gzip"], []),
        ("", "gzip", False, "", [], []),
        ("gzip", "*, gzip", True, "gzip", [], []),
        ("gzip", "*, gzip", False, "gzip", [], []),
        ("gzip", "*, gzip, deflate, br", True, "gzip", [], []),
        ("gzip", "*, gzip, deflate, br", False, "gzip", [], []),
        ("gzip", "*", False, "", [], ["gzip"]),
        ("gzip", "", True, "", [], ["gzip"]),
        ("gzip", "", False, "", [], ["gzip"]),
        ("GZip", "gzIP", True, "gzip", [], []),
        ("gzip", "gzip", False, "gzip", [], []),
        ("", "gzip", True, "gzip", ["gzip"], []),
        ("", "gzip", False, "", [], []),
        (",", "gzip", True, "gzip", ["gzip"], []),
        (",", "gzip", False, "", [], []),
        ("deflate", "gzip", True, "gzip", ["gzip"], ["deflate"]),
        ("deflate", "gzip", False, "", [], ["deflate"]),
        (",gzip,", "gzip", True, "gzip", [], []),
        (",gzip,", "gzip", False, "gzip", [], []),
        ("gzip, br", "gzip", True, "gzip", [], ["br"]),
        ("gzip, br", "gzip", False, "gzip", [], ["br"]),
        ("br, gzip", "gzip", True, "gzip", ["gzip"], ["gzip", "br"]),
        ("br, gzip", "gzip", False, "", [], ["gzip", "br"]),
        ("br, gzip, gzip, br", "gzip", False, "", [], ["br", "gzip", "gzip", "br"]),
        ("gzip", "gzip,br;q=1,deflate;q=0.5 , *;q=0.1", False, "gzip", [], []),
    ],
)
def test_negotiate_encodings(
    content_encoding: str,
    accept_encoding: str,
    auto_gzip: bool,
    expected_encoding: str,
    expected_encoders: list[str],
    expected_decoders: list[str],
):
    result = negotiate_encoding(content_encoding, accept_encoding, auto_gzip)

    assert result.negotiated_encoding == expected_encoding, result
    assert result.encoders == expected_encoders, result
    assert result.decoders == expected_decoders, result


async def test_stream_no_change():

    raw_data = ",".join(uuid4().hex for _ in range(100)).encode()

    async def stream_iter(data: bytes, chunk_size: int = 50):
        chunk = data[:chunk_size]
        while chunk:
            yield chunk
            data = data[chunk_size:]
            chunk = data[:chunk_size]

    stream = negotiated_stream(
        ContentEncodingNegotiation(
            accept_encoding="", negotiated_encoding="", original_encoding="", encoders=[], decoders=[]
        ),
        stream_iter(raw_data),
    )
    result_chunks = []
    async for part in stream:
        result_chunks.append(part)
    result = b"".join(result_chunks)
    assert result == raw_data


def deflate(data, compresslevel=9):
    compress = zlib.compressobj(compresslevel, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    deflated = compress.compress(data)
    deflated += compress.flush()
    return deflated


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)  # see above
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


COMPRESSORS: dict[str, Callable[[bytes], bytes]] = {"gzip": gzip.compress, "deflate": deflate}
DECOMPRESSORS: dict[str, Callable[[bytes], bytes]] = {"gzip": gzip.decompress, "deflate": inflate}


@pytest.mark.parametrize(
    "uncompressed_size, chunk_size, content_encoding, accept_encoding, expected_negotiated, auto_gzip",
    [
        (KiB, 50, "", "gzip", "gzip", True),
        (50 * KiB, KiB - 1, "", "gzip", "gzip", True),
        (KiB, 50, "GZip", "gzIP", "gzip", False),
        (50 * KiB, KiB - 1, "gzip", "gzip", "gzip", False),
        (KiB, 50, "deflate,gzip", "gzip", "", False),
        (50 * KiB, KiB - 1, "deflate,gzip", "gzip", "", False),
        (KiB, 50, "deflate,gzip", "gzip", "gzip", True),
        (50 * KiB, KiB - 1, "deflate,gzip", "gzip", "gzip", True),
        (KiB, 50, "deflate,gzip", "gzip,deflate", "deflate,gzip", True),
        (50 * KiB, KiB - 1, "deflate,gzip", "gzip,deflate", "deflate,gzip", True),
        (KiB, 50, "deflate,gzip", "gzip,deflate", "deflate,gzip", False),
        (50 * KiB, KiB - 1, "deflate,gzip", "gzip,deflate", "deflate,gzip", False),
        (KiB, 50, "deflate,gzip,gzip,deflate", "deflate", "deflate", False),
        (50 * KiB, KiB - 1, "deflate,gzip,gzip,deflate", "deflate", "deflate", False),
        (50 * KiB, KiB - 1, "deflate", "gzip,deflate", "deflate", True),
    ],
)
async def test_stream_negotiation(  # pylint: disable=too-many-locals
    uncompressed_size: int,
    chunk_size: int,
    content_encoding: str,
    accept_encoding: str,
    expected_negotiated: str,
    auto_gzip: bool,
):

    encodings = [enc.strip() for enc in (content_encoding or "").strip().strip(",").split(",") if enc.split()]

    original_data = os.urandom(uncompressed_size)
    raw_data = original_data
    if content_encoding:
        for encoding in encodings:
            raw_data = COMPRESSORS[encoding.lower()](raw_data)

    async def stream_iter(data: bytes):
        chunk = data[:chunk_size]
        while chunk:
            yield chunk
            data = data[chunk_size:]
            chunk = data[:chunk_size]

    negotiated = negotiate_encoding(content_encoding, accept_encoding, auto_gzip)
    stream = negotiated_stream(negotiated, stream_iter(raw_data))
    result_chunks = []
    async for part in stream:
        result_chunks.append(part)

    result = b"".join(result_chunks)

    assert negotiated.negotiated_encoding == expected_negotiated

    for encoding in reversed(negotiated.negotiated_encoding.split(",")):
        if not encoding:
            continue
        result = DECOMPRESSORS[encoding.lower()](result)

    assert result == original_data


@pytest.mark.parametrize(
    "encodings, parts",
    [
        (["gzip"], 4),
        # (["deflate"], 4),
        # (["deflate", "gzip"], 4),
        # (["gzip", "deflate"], 4),
    ],
)
def test_content_encoding(encodings: list[str], parts: int):

    length = 10 * KiB
    raw = os.urandom(length)

    chunk_size = math.ceil(length / parts)
    chunks = []
    remaining = raw
    while remaining:
        chunk = remaining[:chunk_size]
        for encoding in encodings:
            chunk = COMPRESSORS[encoding.lower()](chunk)
        chunks.append(chunk)
        remaining = remaining[chunk_size:]

    decoded = b"".join(chunks)

    for encoding in reversed(encodings):
        decoded = DECOMPRESSORS[encoding.lower()](decoded)

    assert decoded == raw


async def test_stream_non_async():

    raw_data = ",".join(uuid4().hex for _ in range(100)).encode()

    def stream_iter(data: bytes, chunk_size: int = 50):
        chunk = data[:chunk_size]
        while chunk:
            yield chunk
            data = data[chunk_size:]
            chunk = data[:chunk_size]

    stream = negotiated_stream(
        ContentEncodingNegotiation(
            accept_encoding="", negotiated_encoding="", original_encoding="", encoders=[], decoders=[]
        ),
        stream_iter(raw_data),
    )
    result_chunks = []
    async for part in stream:
        result_chunks.append(part)
    result = b"".join(result_chunks)
    assert result == raw_data


async def test_stream_wrapper():
    chunk: bytes = b""

    def iterable():
        yield b"aaa"

    async def aiterable():
        yield b"aaa"

    async for chunk2 in _StreamWrapper(b"aaa"):
        chunk = chunk2

    async for chunk2 in _StreamWrapper([b"aaa"]):
        chunk = chunk2

    assert isinstance(chunk, bytes)

    async for chunk2 in _StreamWrapper(iterable()):
        chunk = chunk2

    assert isinstance(chunk, bytes)

    async for chunk2 in _StreamWrapper(aiterable()):
        chunk = chunk2

    assert isinstance(chunk, bytes)


async def test_async_stream_from_s3(temp_s3_bucket):

    obj = temp_s3_bucket.Object(f"{uuid4().hex}")
    expected = b"A1234567890B"
    obj.put(Body=b"A1234567890B")

    chunks = []
    get_response = obj.get()

    async for chunk in negotiated_stream(
        ContentEncodingNegotiation("", "", "", [], []),
        cast(AsyncIterable[bytes], async_stream_from_s3(get_response, 2)),
    ):
        chunks.append(chunk)

    assert chunks
    assert len(chunks) == 6
    assert b"".join(chunks) == expected
