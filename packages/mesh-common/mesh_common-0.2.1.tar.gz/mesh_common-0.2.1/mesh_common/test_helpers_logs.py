import json
import math
import re
from time import sleep, time
from typing import Callable, Iterable, Optional, cast

import httpx
from botocore.exceptions import ClientError
from mypy_boto3_logs.type_defs import LogStreamTypeDef, OutputLogEventTypeDef
from nhs_aws_helpers import cloudwatchlogs_client

from mesh_common import try_parse_json
from mesh_common.httpx_retry_transport import RetryTransport


class CloudwatchLogsCapture:
    def __init__(
        self,
        log_group: str,
        start_timestamp: Optional[float] = None,
    ):
        self._log_group = log_group
        self._start_timestamp = start_timestamp
        self._logs = cloudwatchlogs_client()
        self.reports: list[dict] = []
        self._last_split = time()

    def __enter__(self):
        self._start_timestamp = self._start_timestamp or time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        return True

    def _split(self) -> float:
        new_ts = time()
        split = new_ts - self._last_split
        self._last_split = new_ts
        return round(split, 6)

    def _get_log_streams(self, timeout: int = 10) -> list[LogStreamTypeDef]:

        end_wait = time() + timeout

        while True:

            try:
                response = self._logs.describe_log_streams(logGroupName=self._log_group)
                streams: list = response["logStreams"]

                while "nextToken" in response:
                    response = self._logs.describe_log_streams(
                        logGroupName=self._log_group,
                        nextToken=response["nextToken"],
                    )
                    streams.extend(response["logStreams"])
                return streams

            except ClientError as client_error:
                if client_error.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise client_error
                if time() > end_wait:
                    raise TimeoutError(f"error waiting for streams for {self._log_group}") from client_error
                sleep(0.1)
                continue

    def find_logs(self, split: Optional[float] = None, json_messages: bool = False):

        since = split or self._start_timestamp or 0

        since_timestamp = math.floor(since) * 1000

        self._split()

        logs: list[dict] = []
        response = self._logs.filter_log_events(logGroupName=self._log_group, startTime=since_timestamp)
        logs.extend(cast(list[dict], response["events"]))

        while "nextToken" in response:
            response = self._logs.filter_log_events(
                logGroupName=self._log_group, startTime=since_timestamp, nextToken=response["nextToken"]
            )
            logs.extend(cast(list[dict], response["events"]))

        self.reports.append(dict(filter_log_events=self._split(), num_logs=len(logs)))

        if json_messages:
            messages = [log.get("message", "").strip() for log in logs if log.get("message", "").startswith("{")]
            json_logs = [json.loads(log) for log in messages]
            return json_logs

        return logs

    def wait_for_logs(
        self,
        min_results: int = 1,
        max_wait: int = 20,
        predicate: Optional[Callable[[dict], bool]] = None,
        json_only: bool = False,
    ):
        end_wait = time() + max_wait

        while True:
            logs = self.find_logs(json_messages=json_only)
            if not json_only:
                logs = [jsonlog for jsonlog in (try_parse_json(log["message"]) for log in logs) if jsonlog]

            if predicate:
                logs = [log for log in logs if predicate(log)]

            self.reports[-1]["filtered_logs"] = len(logs)

            if len(logs) >= min_results:
                return cast(list[dict], logs)

            if time() > end_wait:
                raise TimeoutError(
                    f"failed to match {min_results} json logs for log group {self._log_group} in {max_wait}s",
                    self.reports,
                )

            sleep(0.1)

    @staticmethod
    def match_events(events: Iterable[OutputLogEventTypeDef], match_re: re.Pattern[str]) -> list[dict]:

        matched = []
        for event in events:
            match = match_re.match(event["message"])
            if not match:
                continue
            matched.append(dict(**event, match=match))

        return matched

    @staticmethod
    def find_lambda_invoke_errors(events: Iterable[OutputLogEventTypeDef]) -> list[dict]:

        re_invoke_errors = re.compile(r"^(?P<timestamp>.*)\t(?P<request_id>.*)\tERROR\tInvoke Error \t(?P<detail>.*)$")

        return CloudwatchLogsCapture.match_events(events, re_invoke_errors)


def _search_splunk(
    since: float,
    query: str,
    index: str = "mesh_dev_ops",
    json_only=True,
    splunk_base_uri: str = "https://localhost:8089",
):
    auth = ("admin", "changeme")
    query_data = {
        "search": f'search index="{index}" {query} earliest={math.floor(since)}',
        "output_mode": "json",
    }

    with httpx.Client(
        base_url=splunk_base_uri,
        transport=RetryTransport(
            wrapped_transport=httpx.HTTPTransport(verify=False), retry_status_codes=[204], max_attempts=5
        ),
    ) as client:

        query_url = "/services/search/jobs"

        search_id = client.post(url=query_url, data=query_data, auth=auth).json()["sid"]

        results_response = client.get(f"{query_url}/{search_id}/results?output_mode=json", auth=auth)

    results = results_response.json()["results"]
    if not json_only:
        return [log["_raw"] for log in results]
    events = [jsonlog for jsonlog in (try_parse_json(log["_raw"]) for log in results) if jsonlog]
    return events


def _wait_for_n_splunk_logs(
    since: float,
    initial_query: str,
    index: Optional[str] = None,
    min_results: int = 1,
    max_wait: int = 10,
) -> list[dict]:
    end_wait = time() + max_wait

    index = index or "mesh_dev_ops"

    while True:

        logs = _search_splunk(since, query=initial_query, index=index, json_only=False)

        if len(logs) >= min_results:
            return cast(list[dict], logs)

        if time() > end_wait:
            raise TimeoutError(
                f"failed to match {min_results} json logs for query {initial_query} and index {index} in {max_wait}s"
            )

        sleep(0.1)


def _wait_for_n_splunk_json_logs(
    since: float,
    initial_query: str,
    index: Optional[str] = None,
    min_results: int = 1,
    max_wait: int = 10,
    predicate: Optional[Callable[[dict], bool]] = None,
) -> list[dict]:
    end_wait = time() + max_wait

    index = index or "mesh_dev_ops"

    while True:

        logs = _search_splunk(since, query=initial_query, index=index)
        if predicate:
            logs = [log for log in logs if predicate(log)]

        if len(logs) >= min_results:
            return cast(list[dict], logs)

        if time() > end_wait:
            raise TimeoutError(
                f"failed to match {min_results} json logs for query {initial_query} and index {index} in {max_wait}s"
            )

        sleep(0.1)


def _wait_for_n_cloudwatch_json_logs(
    since: float,
    log_group: Optional[str] = None,
    min_results: int = 1,
    max_wait: int = 20,
    predicate: Optional[Callable[[dict], bool]] = None,
) -> list[dict]:

    log_group = log_group or "/aws/ecs/mesh_api"
    with CloudwatchLogsCapture(log_group=log_group, start_timestamp=since) as capturer:
        logs = capturer.wait_for_logs(min_results=min_results, max_wait=max_wait, predicate=predicate, json_only=True)
        return cast(list[dict], logs)


def search_for_logs(
    since: float,
    logging_provider: str,
    initial_splunk_query: str,
    base_cw_predicate: Callable[[dict], bool],
    filter_predicate: Optional[Callable[[dict], bool]] = None,
    log_group: Optional[str] = None,
    index: Optional[str] = None,
    max_wait: int = 20,
    min_results=1,
):  # pylint: disable=too-many-arguments
    if logging_provider.lower() == "cloudwatch":

        cw_predicate = (
            (lambda log: base_cw_predicate(log) and filter_predicate(log)) if filter_predicate else base_cw_predicate
        )

        return _wait_for_n_cloudwatch_json_logs(
            since,
            log_group=log_group,
            predicate=cw_predicate,
            min_results=min_results,
            max_wait=max_wait,
        )

    if logging_provider.lower() == "splunk":
        return _wait_for_n_splunk_json_logs(
            since,
            index=index,
            initial_query=initial_splunk_query,
            predicate=filter_predicate,
            min_results=min_results,
            max_wait=max_wait,
        )

    raise NotImplementedError(f"searching {logging_provider} for logs not implemented")


def search_logs_for_action(
    since: float,
    logging_provider: str,
    action: str,
    min_results=1,
    predicate: Optional[Callable[[dict], bool]] = None,
    log_group: Optional[str] = None,
    index: Optional[str] = None,
):

    return search_for_logs(
        since=since,
        logging_provider=logging_provider,
        initial_splunk_query=f"action={action}",
        base_cw_predicate=lambda log: log.get("action") == action,
        filter_predicate=predicate,
        min_results=min_results,
        log_group=log_group,
        index=index,
    )


def search_logs_for_log_reference(
    since: float,
    logging_provider: str,
    log_reference: str,
    min_results=1,
    predicate: Optional[Callable[[dict], bool]] = None,
    log_group: Optional[str] = None,
    index: Optional[str] = None,
):
    return search_for_logs(
        since=since,
        logging_provider=logging_provider,
        initial_splunk_query=f"log_reference={log_reference}",
        base_cw_predicate=lambda log: log.get("log_reference") == log_reference,
        filter_predicate=predicate,
        min_results=min_results,
        log_group=log_group,
        index=index,
    )
