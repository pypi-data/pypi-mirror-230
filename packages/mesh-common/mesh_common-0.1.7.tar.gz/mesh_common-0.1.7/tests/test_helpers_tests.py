import os

import pytest

from mesh_common.test_helpers import clear_created_timestamp, temp_env_vars


def test_temp_env_vars():

    assert os.environ.get("AKEY") is None

    with pytest.raises(KeyError):
        _ = os.environ["AKEY"]

    with temp_env_vars(AKEY="123"):

        assert os.environ.get("AKEY") == "123"

    assert os.environ.get("AKEY") is None

    with pytest.raises(KeyError):
        _ = os.environ["AKEY"]


def test_clear_created_timestamp():
    class SomeClass:
        created_timestamp: str

    instance_of_class = SomeClass()
    instance_of_class.created_timestamp = "not none"

    list_items = clear_created_timestamp([instance_of_class])
    assert list_items[0].created_timestamp is None

    set_items = clear_created_timestamp({instance_of_class})
    assert set_items.pop().created_timestamp is None

    frozen_set_items = clear_created_timestamp(frozenset([instance_of_class]))
    assert next(iter(frozen_set_items)).created_timestamp is None

    dictionary_items = clear_created_timestamp({"created_timestamp": "not none"})
    assert dictionary_items["created_timestamp"] is None
