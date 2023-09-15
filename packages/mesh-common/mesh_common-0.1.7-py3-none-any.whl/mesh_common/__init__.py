import asyncio
import json
import threading
import typing
import unicodedata
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from functools import partial
from json import JSONDecodeError
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Iterator,
    Optional,
    TypedDict,
    TypeVar,
    Union,
    cast,
)
from uuid import uuid4

from nhs_context_logging import app_logger


def strtobool(val: Any) -> Optional[bool]:
    if isinstance(val, bool):
        return val
    val = str(val).lower().strip()

    if val in ("y", "yes", "t", "true", "on", "1"):
        return True

    if val in ("n", "no", "f", "false", "off", "0"):
        return False

    return None


def try_strtobool(val: Union[str, int, bool]) -> bool:
    coerced_bool = strtobool(val)

    if coerced_bool in (True, False):
        return coerced_bool

    raise ValueError(f"invalid truth value {val:r}")


async def coro(func: Callable, *args, **kwargs):
    """
        coroutine wrapper to wrap non async calls
    Args:
        func: the function to call
        *args: positional args to pass to fund
        **kwargs: kwargs to pass to func

    Returns:

    """

    return func(*args, **kwargs)


def create_task(func: Callable, *args, **kwargs):
    """
        coroutine wrapper to wrap non async calls
    Args:
        func: the function to call
        *args: positional args to pass to fund
        **kwargs: kwargs to pass to func

    Returns:

    """

    return asyncio.ensure_future(coro(func, *args, **kwargs))


TReturn = TypeVar("TReturn")


async def run_in_executor(func: Callable[..., TReturn], *args, **kwargs) -> TReturn:
    """
        async wrapper for sync code
    Args:
        func: the function to call
        *args: positional args to pass to fund
        **kwargs: kwargs to pass to func

    Returns:

    """
    loop = asyncio.get_running_loop()

    to_execute = partial(func, *args, **kwargs)
    result = typing.cast(TReturn, await loop.run_in_executor(None, to_execute))

    return result


class classproperty(property):  # pylint: disable=invalid-name
    def __init__(self, _getter):
        if not isinstance(_getter, (classmethod, staticmethod)):
            _getter = classmethod(_getter)
        self._getter = _getter
        super().__init__()

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self._getter.__get__(obj, klass)()


def create_internal_id(
    category: Optional[str] = None,
    security_tag: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    unique_part: Optional[str] = None,
):

    timestamp = timestamp or datetime.utcnow()
    unique_part = unique_part or uuid4().hex[:6].upper()

    parts = [timestamp.strftime("%Y%m%d%H%M%S%f"), unique_part]

    if category:
        parts.append(category)

    if security_tag:
        parts.append(security_tag)

    return "_".join(parts)


def is_dataclass_instance(obj) -> bool:
    return is_dataclass(obj) and not isinstance(obj, type)


class _StopIterating(Exception):
    pass


def _try_get_next(iterator: Iterator) -> Any:

    try:
        return next(iterator)
    except StopIteration:
        raise _StopIterating  # pylint: disable=raise-missing-from


TIter_co = TypeVar("TIter_co", covariant=True)


async def to_async_iterator(sync_generator: Iterator[TIter_co]) -> AsyncIterator[TIter_co]:
    while True:
        try:
            yield await run_in_executor(_try_get_next, sync_generator)
        except _StopIterating:
            break


_NoneType = type(None)


def is_optional(the_type: type) -> bool:
    if the_type.__class__.__name__ != "_UnionGenericAlias":
        return False
    args = typing.get_args(the_type)
    if len(args) != 2:
        return False

    return _NoneType in args


def optional_origin_type(original_type: type) -> type:
    """
    if the target type is Optional, this will return the wrapped type
    """
    if original_type.__class__.__name__ != "_UnionGenericAlias":
        return original_type
    args = typing.get_args(original_type)
    if len(args) != 2:
        return original_type

    args = tuple(arg for arg in args if arg != _NoneType)
    if len(args) != 1:
        return original_type
    return typing.cast(type, args[0])


def ensure_text(string, encoding="utf-8", errors="strict"):

    if isinstance(string, str):
        return string

    if isinstance(string, bytes):
        return string.decode(encoding, errors)

    raise TypeError(f"not expecting type '{type(string)}'")


def strip_non_printable_ascii(original: Optional[str]) -> Optional[str]:

    if not original:
        return original

    return "".join(
        character for character in ensure_text(original, encoding="utf-8", errors="strict") if 31 < ord(character) < 128
    )


def remove_control_characters(original: Optional[str]) -> Optional[str]:

    if not original:
        return original

    return "".join(
        character
        for character in ensure_text(original, encoding="utf-8", errors="strict")
        if unicodedata.category(character)[0] != "C"
    )


_NHS_CHECK_DIGIT_WEIGHTINGS = [10, 9, 8, 7, 6, 5, 4, 3, 2]


def _calculate_check_digit(nhs_num: str) -> Optional[int]:
    digits = map(int, nhs_num[:9])

    check_digit_sum = sum(x * y for x, y in zip(digits, _NHS_CHECK_DIGIT_WEIGHTINGS))

    check_digit = 11 - (check_digit_sum % 11)

    if check_digit == 11:
        return 0

    if check_digit == 10:
        return None  # invalid check digit

    return check_digit


def is_valid_nhs_number(nhs_num: str, palindrome_check=False) -> bool:
    nhs_num = (nhs_num or "").replace(" ", "").replace("-", "").strip()
    if not nhs_num:
        return False

    if len(nhs_num) != 10 or not nhs_num.isdigit():
        return False

    # palindrome check - disabled by default
    if palindrome_check and nhs_num[:5] == list(reversed(nhs_num[-5:])):
        return False

    return int(nhs_num[-1]) == _calculate_check_digit(nhs_num)


def try_parse_json(message: str) -> Optional[dict]:
    try:
        return cast(dict, json.loads(message))
    except JSONDecodeError:
        return None


class AsyncLockable:
    def __init__(self):
        self._sync_lock = threading.Lock()
        self._lock = None

    @property
    def lock(self):

        if self._lock is not None:
            return self._lock

        with self._sync_lock:
            if self._lock is not None:
                return self._lock
            self._lock = asyncio.Lock()
            return self._lock


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden,too-many-return-statements

        if o is None:
            return o

        if isinstance(o, (set, frozenset)):
            return list(o)

        if isinstance(o, (date, datetime)):
            return o.isoformat()

        if is_dataclass(o):
            return asdict(o)

        if hasattr(o, "as_dict"):
            return o.as_dict()

        if isinstance(o, Decimal):
            as_str = str(o)
            return float(as_str) if "." in as_str else int(as_str)

        return json.JSONEncoder.default(self, o)


ModelKey = TypedDict("ModelKey", {"pk": str, "sk": str})


setup_file_logger = partial(app_logger.setup_file_log, log_dir="/var/log/mesh", internal_id_factory=create_internal_id)
setup_app_logger = partial(app_logger.setup, internal_id_factory=create_internal_id)
