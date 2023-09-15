import os
import traceback

import nhs_aws_helpers
from botocore.config import Config
from botocore.retries.standard import RetryContext
from nhs_context_logging import app_logger

retry_config = Config(
    connect_timeout=float(os.environ.get("BOTO_CONNECT_TIMEOUT", "1")),
    read_timeout=float(os.environ.get("BOTO_READ_TIMEOUT", "1")),
    max_pool_connections=int(os.environ.get("BOTO_MAX_POOL_CONNECTIONS", "10")),
    retries={
        "mode": os.environ.get("BOTO_RETRIES_MODE", "standard"),  # type: ignore[typeddict-item]
        "total_max_attempts": int(os.environ.get("BOTO_RETRIES_TOTAL_MAX_ATTEMPTS", "10")),
    },
)


def _on_backoff(backoff: int, context: RetryContext):

    app_logger.warn(
        dict(
            message="backing_off",
            backoff=backoff,
            retry_context=dict(
                attempt_number=context.attempt_number,
                request_context=context.request_context,
                http_response=context.http_response,
                caught_exception=context.caught_exception,
                operation_model=context.operation_model,
                parsed_response=context.parsed_response,
                error_code=context.get_error_code(),
                metadata=context.get_retry_metadata(),
            ),
        )
    )


def _on_error_received(**kwargs):

    app_logger.warn(dict(message="aws_error_response_received", traceback="".join(traceback.format_stack()), **kwargs))


def _post_create_aws(boto_module: str, _: str, client):
    if boto_module != "s3":
        return
    nhs_aws_helpers.register_retry_handler(client, on_error=_on_error_received, on_backoff=_on_backoff)


def setup_aws_retries():
    nhs_aws_helpers.register_config_default("s3", retry_config)
    nhs_aws_helpers.post_create_client(_post_create_aws)
