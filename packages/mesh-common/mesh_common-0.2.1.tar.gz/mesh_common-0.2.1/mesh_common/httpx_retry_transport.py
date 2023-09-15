import random
from datetime import datetime
from time import sleep
from typing import Iterable, Mapping, Optional, Union, cast

import httpx
from dateutil.parser import isoparse


class RetryTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):

    DEFAULT_RETRYABLE_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    DEFAULT_RETRYABLE_STATUS_CODES = frozenset([413, 429, 503, 504])
    DEFAULT_MAX_BACKOFF_WAIT = 60

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        wrapped_transport: Union[httpx.BaseTransport, httpx.AsyncBaseTransport],
        max_attempts: int = 10,
        max_backoff_wait: float = DEFAULT_MAX_BACKOFF_WAIT,
        backoff_factor: float = 0.1,
        jitter_ratio: float = 0.1,
        respect_retry_after_header: bool = True,
        retryable_methods: Optional[Iterable[str]] = None,
        retry_status_codes: Optional[Iterable[int]] = None,
    ) -> None:
        self.wrapped_transport = wrapped_transport
        if jitter_ratio < 0 or jitter_ratio > 0.5:
            raise ValueError(f"jitter ratio should be between 0 and 0.5, actual {jitter_ratio}")

        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.respect_retry_after_header = respect_retry_after_header
        self.retryable_methods = frozenset(retryable_methods) if retryable_methods else self.DEFAULT_RETRYABLE_METHODS
        self.retry_status_codes = (
            frozenset(retry_status_codes) if retry_status_codes else self.DEFAULT_RETRYABLE_STATUS_CODES
        )
        self.jitter_ratio = jitter_ratio
        self.max_backoff_wait = max_backoff_wait

    def _calculate_sleep(self, attempts_made: int, headers: Union[httpx.Headers, Mapping[str, str]]) -> float:

        retry_after_header = (headers.get("Retry-After") or "").strip()
        if self.respect_retry_after_header and retry_after_header:
            if retry_after_header.isdigit():
                return float(retry_after_header)

            try:
                parsed_date = isoparse(retry_after_header).astimezone()  # converts to local time
                diff = (parsed_date - datetime.now().astimezone()).total_seconds()
                if diff > 0:
                    return min(diff, self.max_backoff_wait)
            except ValueError:
                pass

        # exponential backoff  e.g 0.1, 0.2, 0.4
        backoff = self.backoff_factor * (2 ** (attempts_made - 1))
        # jitter adjustment  e.g.  0.1 * 1.1 = 0.11 .. 4 * 0.9 = 3.6
        jitter_ratio = 1 + (random.choice([1, -1]) * self.jitter_ratio)
        total_backoff = backoff * jitter_ratio

        return float(min(total_backoff, self.max_backoff_wait))

    def max_possible_duration(self, request_timeout: float):

        tot_request_timeout = request_timeout * self.max_attempts
        tot_backoff = sum(
            min((self.backoff_factor * (2**i) * (1 + self.jitter_ratio)), self.max_backoff_wait)
            for i in range(self.max_attempts)
        )
        return tot_request_timeout + tot_backoff

    def handle_request(self, request: httpx.Request) -> httpx.Response:

        transport = cast(httpx.BaseTransport, self.wrapped_transport)

        response = transport.handle_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:

            if remaining_attempts < 1 or response.status_code not in self.retry_status_codes:
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = transport.handle_request(request)

            attempts_made += 1
            remaining_attempts -= 1

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:

        transport = cast(httpx.AsyncBaseTransport, self.wrapped_transport)

        response = await transport.handle_async_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:

            if remaining_attempts < 1 or response.status_code not in self.retry_status_codes:
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = await transport.handle_async_request(request)

            attempts_made += 1
            remaining_attempts -= 1
