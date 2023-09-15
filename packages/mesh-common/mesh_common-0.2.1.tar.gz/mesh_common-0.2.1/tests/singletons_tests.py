import asyncio
from uuid import uuid4

import pytest

from mesh_common import coro, singletons
from mesh_common.concurrency import concurrent_tasks


@pytest.mark.parametrize(
    "key, expected",
    [
        ("same key", "value1"),
        ("same key", "value2"),
    ],
)
def test_sync_create_and_resolve(key, expected):

    calls = 0

    def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    resolved = singletons.resolve_sync(key, get_thing)

    assert resolved == expected

    singletons.resolve_sync(key, get_thing)


@pytest.mark.parametrize(
    "key, expected",
    [
        ("same key", "value1"),
        ("same key", "value2"),
    ],
)
async def test_async_create_and_resolve(key, expected):

    calls = 0

    async def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    resolved = await singletons.resolve(key, get_thing)

    assert resolved == expected

    await singletons.resolve(key, get_thing)


async def test_async_parallel_resolve():

    calls = 0

    key = uuid4().hex
    expected = uuid4().hex

    async def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    resolved = await asyncio.gather(
        singletons.resolve(key, get_thing),
        singletons.resolve(key, get_thing),
        singletons.resolve(key, get_thing),
        singletons.resolve(key, get_thing),
    )

    assert resolved == [expected, expected, expected, expected]


async def test_async_resolve_dependants():

    calls = 0

    key1 = uuid4().hex
    key2 = uuid4().hex
    expected = uuid4().hex

    async def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    async def get_thing_outer():
        value = await singletons.resolve(key2, get_thing)
        return value

    resolved = await singletons.resolve(key1, get_thing_outer)
    assert resolved == expected


def test_sync_resolve_dependants():

    calls = 0

    key1 = uuid4().hex
    key2 = uuid4().hex
    expected = uuid4().hex

    def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    def get_thing_outer():
        value = singletons.resolve_sync(key2, get_thing)
        return value

    resolved = singletons.resolve_sync(key1, get_thing_outer)
    assert resolved == expected


def test_sync_resolve_dependants_recursive():

    key1 = uuid4().hex
    key2 = uuid4().hex

    def get_thing():
        resolved = singletons.resolve_sync(key1, get_thing_outer)
        return resolved

    def get_thing_outer():
        value = singletons.resolve_sync(key2, get_thing)
        return value

    with pytest.raises(RecursionError):
        singletons.resolve_sync(key1, get_thing_outer)


async def test_async_resolve_dependants_recursive():

    key1 = uuid4().hex
    key2 = uuid4().hex

    async def get_thing():
        resolved = await singletons.resolve(key1, get_thing_outer)
        return resolved

    async def get_thing_outer():
        value = await singletons.resolve(key2, get_thing)
        return value

    with pytest.raises(RecursionError):
        await singletons.resolve(key1, get_thing_outer)


def test_thread_resolve_in_parallel():

    calls = 0

    key1 = uuid4().hex
    key2 = uuid4().hex
    expected = uuid4().hex

    def get_thing():
        nonlocal calls
        if calls > 0:
            raise ValueError("eek")
        calls += 1
        return expected

    def get_thing_outer():
        value = singletons.resolve_sync(key2, get_thing)
        return value

    tests = 4
    tasks = [(f"{i}", singletons.resolve_sync, (key1, get_thing_outer)) for i in range(tests)]
    all_expected = [expected for _ in range(tests)]
    resolved = list(concurrent_tasks(tasks).values())  # type: ignore[arg-type]

    assert resolved == all_expected


async def test_async_resolve_in_parallel():

    for _ in range(10):

        key1 = uuid4().hex
        key2 = uuid4().hex
        expected = uuid4().hex

        generator = iter([expected, uuid4().hex, uuid4().hex, uuid4().hex, uuid4().hex, uuid4().hex])

        async def get_thing():
            return next(generator)

        calls = 0

        async def get_thing_outer():
            nonlocal calls
            calls += 1
            value = await singletons.resolve(key2, get_thing)
            return value

        def sync_get_thing():
            return next(generator)

        def sync_get_thing_outer():
            nonlocal calls
            calls += 1
            value = singletons.resolve_sync(key2, sync_get_thing)
            return value

        resolved = await asyncio.gather(
            coro(lambda: singletons.resolve_sync(key1, sync_get_thing_outer)),
            singletons.resolve(key1, get_thing_outer),
            singletons.resolve(key1, get_thing_outer),
            singletons.resolve(key1, get_thing_outer),
        )

        assert calls == 1

        assert resolved == [expected, expected, expected, expected]


async def test_async_gather():

    expected = {uuid4().hex, uuid4().hex, uuid4().hex, uuid4().hex}

    generator = iter(expected)

    async def get_thing():
        return next(generator)

    resolved = await asyncio.gather(
        get_thing(),
        get_thing(),
        get_thing(),
        get_thing(),
    )

    assert set(resolved) == expected
