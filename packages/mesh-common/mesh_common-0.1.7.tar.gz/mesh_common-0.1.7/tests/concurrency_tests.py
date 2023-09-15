from uuid import uuid4

import pytest
from nhs_context_logging import log_action, temporary_global_fields

from mesh_common.concurrency import ConcurrentExceptions, concurrent_tasks


def assert_single_internal_id(log_capture: tuple):
    internal_ids = {line["internal_id"] for line in (log_capture[0] + log_capture[1])}
    assert len(internal_ids) == 1, internal_ids


def test_no_tasks(log_capture: tuple):
    std_out, std_err = log_capture

    items: list[int] = []

    @log_action()
    def task(item: int):
        return item * 13

    with log_action("wrapper"):
        results = concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    assert len(results) == 0

    assert len(std_out) == 1
    assert len(std_err) == 0
    assert std_out[0]["action"] == "wrapper"

    assert_single_internal_id(log_capture)


def test_single_task(log_capture: tuple):
    std_out, std_err = log_capture

    items: list[int] = [1]

    @log_action()
    def task(item: int):
        return item * 13

    with log_action("wrapper"):
        results = concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    assert len(results) == 1
    assert results["0"] == 13

    assert len(std_out) == 2
    assert len(std_err) == 0
    assert (std_out[0]["action"], std_out[0]["action_status"]) == ("task", "succeeded")
    assert (std_out[1]["action"], std_out[1]["action_status"]) == ("wrapper", "succeeded")

    assert_single_internal_id(log_capture)


def test_single_task_single_error(log_capture: tuple):
    std_out, std_err = log_capture

    items: list[int] = [1]

    @log_action()
    def task(item: int):
        raise ValueError(f"Failed task {item}")

    with pytest.raises(ValueError) as ex:
        with log_action("wrapper"):
            concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    assert str(ex.value) == "Failed task 1"

    assert len(std_out) == 0
    assert len(std_err) == 2
    assert (std_err[0]["action"], std_err[0]["action_status"]) == ("task", "failed")
    assert (std_err[1]["action"], std_err[1]["action_status"]) == ("wrapper", "failed")

    assert_single_internal_id(log_capture)


def test_multiple_tasks(log_capture: tuple):
    std_out, std_err = log_capture

    global_id = uuid4().hex

    items: list[int] = [1, 2, 3]

    @log_action()
    def task(item: int):
        return item * 13

    with log_action("wrapper"):
        with temporary_global_fields(global_id=global_id):
            results = concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    assert len(results) == 3
    assert results["0"] == 13
    assert results["1"] == 26
    assert results["2"] == 39

    assert len(std_out) == len(items) + 1
    assert len(std_err) == 0
    task_logs = [line for line in std_out if line["action"] == "task" and line["action_status"] == "succeeded"]
    assert len(task_logs) == len(items)

    assert (std_out[-1]["action"], std_out[-1]["action_status"]) == ("wrapper", "succeeded")

    assert_single_internal_id(log_capture)

    actual_global_ids = {line["global_id"] for line in std_out + std_err if line["action"] == "task"}
    assert len(actual_global_ids) == 1
    assert actual_global_ids == {global_id}


def test_multiple_tasks_single_error(log_capture: tuple):
    std_out, std_err = log_capture

    global_id = uuid4().hex

    items: list[int] = [1, 2, 3]

    @log_action()
    def task(item: int):
        if item == 3:
            raise ValueError(f"Failed task {item}")

        return item * 13

    with pytest.raises(ValueError) as ex:
        with log_action("wrapper"):
            with temporary_global_fields(global_id=global_id):
                concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    assert str(ex.value) == "Failed task 3"

    assert len(std_out) == len(items) - 1
    assert len(std_err) == 2
    task_logs_succeeded = [
        line for line in std_out if line["action"] == "task" and line["action_status"] == "succeeded"
    ]
    task_logs_failed = [line for line in std_err if line["action"] == "task" and line["action_status"] == "failed"]
    assert len(task_logs_succeeded) == len(items) - 1
    assert len(task_logs_failed) == 1

    assert (std_err[-1]["action"], std_err[-1]["action_status"]) == ("wrapper", "failed")

    assert_single_internal_id(log_capture)

    actual_global_ids = {line["global_id"] for line in std_out + std_err if line["action"] == "task"}
    assert len(actual_global_ids) == 1
    assert actual_global_ids == {global_id}


def test_multiple_tasks_all_error(log_capture: tuple):
    std_out, std_err = log_capture

    global_id = uuid4().hex

    items: list[int] = [1, 2, 3]

    @log_action()
    def task(item: int):
        raise ValueError(f"Failed task {item}")

    with pytest.raises(ConcurrentExceptions) as ex:
        with log_action("wrapper"):
            with temporary_global_fields(global_id=global_id):
                concurrent_tasks([(f"{idx}", task, (item,)) for idx, item in enumerate(items)])

    exceptions = ex.value.exceptions
    assert len(exceptions) == len(items)
    for idx, item in enumerate(items):
        assert str(exceptions[f"{idx}"]) == f"Failed task {item}"

    assert len(std_out) == 0
    assert len(std_err) == len(items) + 1
    task_logs_succeeded = [
        line for line in std_out if line["action"] == "task" and line["action_status"] == "succeeded"
    ]
    task_logs_failed = [line for line in std_err if line["action"] == "task" and line["action_status"] == "failed"]
    assert len(task_logs_succeeded) == 0
    assert len(task_logs_failed) == len(items)

    assert (std_err[-1]["action"], std_err[-1]["action_status"]) == ("wrapper", "failed")

    assert_single_internal_id(log_capture)

    actual_global_ids = {line["global_id"] for line in std_out + std_err if line["action"] == "task"}
    assert len(actual_global_ids) == 1
    assert actual_global_ids == {global_id}
