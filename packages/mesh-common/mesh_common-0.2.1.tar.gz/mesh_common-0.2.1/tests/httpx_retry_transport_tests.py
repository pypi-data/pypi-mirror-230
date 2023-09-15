from datetime import datetime, timedelta, timezone
from typing import Callable
from unittest.mock import MagicMock

import httpx
import pytest
from dateutil.relativedelta import relativedelta

from mesh_common.httpx_retry_transport import RetryTransport


@pytest.mark.parametrize(
    "retry_after, attempts_made, expected_approx_in, respect_retry_after_header",
    [
        ((lambda now: "10"), 1, {10}, True),
        (
            ((lambda now: (now + relativedelta(seconds=10)).astimezone(timezone(timedelta(hours=6))).isoformat())),
            1,
            {9, 10},
            True,
        ),
        ((lambda now: (now + relativedelta(seconds=30)).isoformat()), 1, {29, 30}, True),
        ((lambda now: (now + relativedelta(hours=10)).isoformat()), 1, {RetryTransport.DEFAULT_MAX_BACKOFF_WAIT}, True),
        ((lambda now: (now + relativedelta(seconds=-10)).isoformat()), 1, {0}, True),
        ((lambda now: (now + relativedelta(seconds=10)).isoformat()), 1, {0}, False),
    ],
)
def test_calculate_sleep_retry_after(
    retry_after: Callable[[datetime], str],
    attempts_made: int,
    expected_approx_in: set[float],
    respect_retry_after_header: bool,
):
    retry_after_header = retry_after(datetime.now())
    transport = RetryTransport(
        wrapped_transport=httpx.HTTPTransport(), respect_retry_after_header=respect_retry_after_header
    )

    headers = {"Retry-After": retry_after_header}

    actual = transport._calculate_sleep(attempts_made, headers)  # pylint: disable=protected-access

    assert round(actual) in expected_approx_in


@pytest.mark.parametrize(
    "attempts_made, backoff_factor, jitter_ratio, max_backoff_wait, expected_one_of",
    [
        (1, 0.1, 0, 10, {0.1}),  # basic exponential progression no jitter
        (2, 0.1, 0, 10, {0.2}),
        (3, 0.1, 0, 10, {0.4}),
        (3, 1, 0, 1, {1}),  # ensure max_backoff_wait takes precedence
        (3, 0.1, 0.1, 10, {0.36, 0.44}),  # jitter ratio applied
    ],
)
def test_calculate_sleep_backoff_jitter(
    attempts_made: int, backoff_factor: float, jitter_ratio: float, max_backoff_wait: float, expected_one_of: set[float]
):

    transport = RetryTransport(
        wrapped_transport=httpx.HTTPTransport(),
        backoff_factor=backoff_factor,
        jitter_ratio=jitter_ratio,
        max_backoff_wait=max_backoff_wait,
    )

    actual = round(transport._calculate_sleep(attempts_made, {}), 4)  # pylint: disable=protected-access

    assert actual in expected_one_of


@pytest.mark.parametrize(
    "request_timeout, max_attempts, backoff_factor, jitter_ratio, max_backoff_wait, expected",
    [
        (0, 1, 0, 0, 0, 0),
        (1, 1, 0, 0.1, 1, 1),
        (1, 2, 1, 0.1, 2, 5.1),
    ],
)
def test_max_possible_duration(
    request_timeout: float,
    max_attempts: int,
    backoff_factor: float,
    jitter_ratio: float,
    max_backoff_wait: float,
    expected: float,
):

    transport = RetryTransport(
        wrapped_transport=httpx.HTTPTransport(),
        max_attempts=max_attempts,
        backoff_factor=backoff_factor,
        jitter_ratio=jitter_ratio,
        max_backoff_wait=max_backoff_wait,
    )

    actual = transport.max_possible_duration(request_timeout)

    assert actual == expected


def test_retry_sync_transport():

    mock_handler = MagicMock()
    mock_handler.return_value = httpx.Response(404)

    with httpx.Client(
        base_url="https://example.org",
        transport=RetryTransport(
            wrapped_transport=httpx.MockTransport(mock_handler),
            retry_status_codes=[404],
            max_attempts=2,
            max_backoff_wait=1,
        ),
    ) as client:

        response = client.get("/")
        assert mock_handler.call_count == 2
        assert response.status_code == 404


async def test_retry_async_transport():

    mock_handler = MagicMock()
    mock_handler.return_value = httpx.Response(404)

    async with httpx.AsyncClient(
        base_url="https://example.org",
        transport=RetryTransport(
            wrapped_transport=httpx.MockTransport(mock_handler),
            retry_status_codes=[404],
            max_attempts=2,
            max_backoff_wait=1,
        ),
    ) as client:

        response = await client.get("/")
        assert mock_handler.call_count == 2
        assert response.status_code == 404
