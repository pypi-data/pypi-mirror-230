import logging
from typing import cast

from mypy_boto3_sqs.service_resource import Queue, SQSServiceResource
from nhs_aws_helpers import sqs_resource
from nhs_context_logging import add_fields, log_action

from mesh_common import AsyncLockable, run_in_executor


class SQSHelper(AsyncLockable):
    def __init__(self):
        super().__init__()
        self._queues: dict[str, Queue] = {}
        self._resource: SQSServiceResource = sqs_resource()

    @property
    def resource(self) -> SQSServiceResource:
        return self._resource

    @log_action(log_level=logging.DEBUG, log_args=["queue_name"])
    async def _get_queue(self, queue_name: str) -> Queue:
        queue = self._queues.get(queue_name)
        if queue:
            return queue

        async with self.lock:

            queue = self._queues.get(queue_name)
            if not queue:
                queue = await run_in_executor(self._resource.get_queue_by_name, QueueName=queue_name)
                self._queues[queue_name] = cast(Queue, queue)

        return cast(Queue, queue)

    @log_action(log_args=["queue_name"])
    async def send_message(self, queue_name: str, **kwargs) -> str:

        queue = await self._get_queue(queue_name)
        add_fields(queue_url=queue.url)

        result = await run_in_executor(queue.send_message, **kwargs)
        add_fields(sqs_message_id=result["MessageId"])
        return result["MessageId"]

    @log_action(log_level=logging.DEBUG)
    async def get_queue(self, queue_name) -> Queue:
        return await self._get_queue(queue_name)
