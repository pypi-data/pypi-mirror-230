import json
from typing import cast

from cryptography.fernet import Fernet

from mesh_common import singletons
from mesh_common.env_config import EnvConfig


def _create_fernet() -> Fernet:
    config = EnvConfig()
    encoder = Fernet(config.fernet_key)
    return encoder


def encode_dict(data: dict, encoding: str = "utf-8") -> str:
    fernet = cast(Fernet, singletons.resolve_sync(Fernet, _create_fernet))
    return fernet.encrypt(json.dumps(data).encode(encoding=encoding)).decode()


def decode_dict(data: str, encoding: str = "utf-8") -> dict:
    fernet = cast(Fernet, singletons.resolve_sync(Fernet, _create_fernet))
    json_str = fernet.decrypt(data.encode(encoding=encoding)).decode()
    return cast(dict, json.loads(json_str))
