import asyncio
import base64
import contextlib
import json
import os
from datetime import datetime
from json import JSONDecodeError
from time import sleep, time
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    TypeVar,
    cast,
)

from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
from mypy_boto3_sqs.service_resource import Queue

from mesh_common import try_parse_json


@contextlib.contextmanager
def temp_env_vars(**kwargs):
    """
    Temporarily set the process environment variables.
    >>> with temp_env_vars(PLUGINS_DIR=u'test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True
    >>> "PLUGINS_DIR" in os.environ
    """
    old_environ = dict(os.environ)
    kwargs = {k: str(v) for k, v in kwargs.items()}
    os.environ.update(**kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


async def async_gen_to_bytes(async_gen: AsyncGenerator[bytes, None]) -> bytes:
    b_sent = b""
    async for byte in async_gen:
        b_sent += byte

    return b_sent


async def wait_for_task(task: asyncio.Task, raise_error_on_timeout: bool, timeout: float = 1):
    try:
        await asyncio.wait_for(task, timeout=timeout)
    except asyncio.TimeoutError as error:
        # (this could get thrown if you debugged the task and slowed it down)
        if raise_error_on_timeout:
            raise AssertionError("task timed out") from error


def sync_lambda_invocation_successful(response: InvocationResponseTypeDef) -> tuple[str, list[str]]:

    assert response["StatusCode"] == 200

    raw_logs = ""
    logs = []

    if "LogResult" in response:
        logs = useful_lambda_logs(response)
        raw_logs = "\n".join(logs)

    function_error = response.get("FunctionError")
    if "Payload" not in response:
        raise AssertionError(f"lambda failed: {function_error}")

    payload = response["Payload"].read().decode()
    if not function_error:
        return payload, logs

    try:
        parsed = json.loads(payload)
        if "errorMessage" in payload:
            parsed["errorMessage"] = parsed["errorMessage"].split("\n")
        payload = json.dumps(parsed, indent=4)
    except JSONDecodeError:
        pass
    raise AssertionError(f"lambda failed: {function_error}\n{payload}\n{raw_logs}")


def sync_json_lambda_invocation_successful(
    response: InvocationResponseTypeDef, logs_predicate: Optional[Callable[[dict], bool]] = None
) -> tuple[dict, list[dict]]:
    raw_payload, _ = sync_lambda_invocation_successful(response)
    payload = json.loads(raw_payload)

    json_logs = json_lambda_logs(response, predicate=logs_predicate)

    return payload, json_logs


def lambda_log_lines(res: InvocationResponseTypeDef) -> list[str]:

    logs = base64.b64decode(res["LogResult"]).decode().strip().split("\n")
    return logs


def useful_lambda_logs(res: InvocationResponseTypeDef) -> list[str]:

    logs = lambda_log_lines(res)
    return [
        line
        for line in logs
        if line and not line.startswith("START ") and not line.startswith("END ") and not line.startswith("REPORT ")
        if line
    ]


def json_lambda_logs(res: InvocationResponseTypeDef, predicate: Optional[Callable[[dict], bool]] = None) -> list[dict]:

    useful_logs = useful_lambda_logs(res)

    return [
        log for log in (try_parse_json(line) for line in useful_logs) if log and (predicate is None or predicate(log))
    ]


def timestamps_are_within_a_second(time1: Optional[datetime], time2: Optional[datetime]) -> bool:
    if not time1 or not time2:
        raise ValueError("cannot compare null date times")
    return 0 <= abs((time1 - time2).total_seconds()) < 1


TReturn_co = TypeVar("TReturn_co", covariant=True)


def wait_for_state(
    getter: Callable[[], TReturn_co],
    predicate: Callable[[TReturn_co], bool],
    timeout: float = 5,
    allow_none: bool = False,
    sleep_seconds: float = 0.1,
) -> TReturn_co:

    timeout_at = time() + timeout
    while True:

        result = getter()
        if (allow_none or result) and predicate(result):
            return result

        sleep(sleep_seconds)
        if time() >= timeout_at:
            raise TimeoutError("timeout waiting for expected state")


async def async_wait_for_state(
    getter: Callable[[], Awaitable[TReturn_co]],
    predicate: Callable[[TReturn_co], bool],
    timeout: float = 5,
    allow_none: bool = False,
) -> TReturn_co:

    timeout_at = time() + timeout
    while True:

        result = await getter()
        if (allow_none or result) and predicate(result):
            return result

        sleep(0.1)
        if time() >= timeout_at:
            raise TimeoutError("timeout waiting for expected state")


async def wait_for_item_matching(
    items: Iterable[TReturn_co], predicate: Callable[[TReturn_co], Any], timeout: float = 5
) -> TReturn_co:

    timeout_at = time() + timeout
    while True:
        if time() >= timeout_at:
            raise TimeoutError("timeout waiting for expected state")

        matched = next((item for item in items if predicate(item)), None)
        if not matched:
            await asyncio.sleep(0.1)
            continue

        return matched


def read_sqs_json_messages(queue: Queue, predicate: Optional[Callable[[dict], bool]] = None, **kwargs) -> list[dict]:

    defaults = {"MaxNumberOfMessages": 10, "WaitTimeSeconds": 0}
    if kwargs:
        defaults.update(kwargs)

    messages = queue.receive_messages(**defaults)  # type: ignore[arg-type]

    if not messages:
        return []

    parsed = cast(list[dict], [json.loads(message.body) for message in messages])

    if not predicate:
        return parsed

    return [msg for msg in parsed if predicate(msg)]


def clear_last_modified(item_or_items: Any):
    if not item_or_items:
        return item_or_items

    if isinstance(item_or_items, (list, set, frozenset)):
        for item in item_or_items:
            if hasattr(item, "last_modified"):
                item.last_modified = None
        return item_or_items

    if hasattr(item_or_items, "last_modified"):
        item_or_items.last_modified = None

    return item_or_items


def clear_created_timestamp(item_or_items: Any):
    """
    note: this function isn't recursive.
    """
    if not item_or_items:
        return item_or_items

    if isinstance(item_or_items, (list, set, frozenset)):
        for item in item_or_items:
            if hasattr(item, "created_timestamp"):
                item.created_timestamp = None
        return item_or_items

    if hasattr(item_or_items, "created_timestamp"):
        item_or_items.created_timestamp = None

    if isinstance(item_or_items, dict):
        if item_or_items.get("created_timestamp", None) is not None:
            item_or_items["created_timestamp"] = None

    return item_or_items
