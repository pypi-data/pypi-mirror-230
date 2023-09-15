import pytest

from mesh_common.env_config import EnvConfig
from mesh_common.test_helpers import temp_env_vars


@pytest.fixture(scope="function", name="env_config_tests", autouse=True)
def temp_everything():
    with temp_env_vars(
        MESH_FEATURE_TEST_FEATURE_DISABLED="0",
        MESH_FEATURE_TEST_FEATURE="true",
        MESH_S3_BUCKET="brian",
    ):
        yield


def test_env_config():
    config = EnvConfig()

    assert config.feature.test_feature
    assert not config.feature.test_feature_disabled
    assert config.s3_bucket == "brian"


def test_env_config_override():
    config = EnvConfig(s3_bucket="mary", feature_overrides={"test_feature": False, "test_feature_disabled": True})

    assert not config.feature.test_feature
    assert config.feature.test_feature_disabled
    assert config.s3_bucket == "mary"


def test_find_env_keys():

    with temp_env_vars(
        MESH_SERVER_CA3="jim",
        MESH_SERVER_CA1="bob",
        MESH_SERVER_CA2="vic",
        MESH_SERVER_CAA="geoffa",
        MESH_SERVER_CAB="geoffb",
        MESH_CLIENT_CAB="thing!",
    ):
        config = EnvConfig()
        keys = list(config.keys(lambda x: x.startswith("server_ca")))
        assert keys == ["server_ca1", "server_ca2", "server_ca3", "server_caa", "server_cab"]


def test_find_env_values():

    with temp_env_vars(
        MESH_SERVER_CA3="jim",
        MESH_SERVER_CA1="bob",
        MESH_SERVER_CA2="vic",
        MESH_SERVER_CAA="geoffa",
        MESH_SERVER_CAB="geoffb",
        MESH_CLIENT_CAB="thing!",
    ):
        config = EnvConfig()
        values = list(config.values(lambda x: x.startswith("server_ca")))
        assert values == ["bob", "vic", "jim", "geoffa", "geoffb"]
