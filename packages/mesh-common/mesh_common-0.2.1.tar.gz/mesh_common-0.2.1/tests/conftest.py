import os

import pytest  # noqa: F401
from nhs_aws_helpers.fixtures import *  # noqa: F403, F401
from nhs_context_logging.fixtures import *  # noqa: F403, F401

from mesh_common import setup_app_logger, singletons
from mesh_common.fixtures import *  # noqa: F403, F401


@pytest.fixture(scope="session", autouse=True)
def global_setup():
    os.environ.setdefault("LOCAL_MODE", "True")
    os.environ.setdefault("AWS_ENDPOINT_URL", "http://localhost:4566")
    os.environ.setdefault("env", "local")
    os.environ.setdefault("MESH_ENV", "local")

    setup_app_logger("pytest")


@pytest.fixture(scope="function", autouse=True)
def reset_storage():
    singletons.clear()
