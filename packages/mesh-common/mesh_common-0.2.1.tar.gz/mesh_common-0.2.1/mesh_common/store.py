import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Final,
    Generic,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    cast,
)

from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.type_defs import (
    QueryOutputTableTypeDef,
    TransactGetItemTypeDef,
    UpdateItemOutputTableTypeDef,
)
from nhs_aws_helpers.dynamodb_model_store.base_model import (
    BaseModel,
    model_properties_cache,
    serialised_property,
)
from nhs_aws_helpers.dynamodb_model_store.base_model_store import (
    BaseModelStore,
    PagedItems,
    TBaseModel_co,
)
from nhs_context_logging import add_fields, log_action

from mesh_common import ModelKey, is_dataclass_instance


class BaseMeshModel(BaseModel[ModelKey]):
    _index_model_type: bool = True
    _model_key_type = ModelKey


@dataclass(kw_only=True)
class MeshModel(BaseMeshModel):
    # pk: str
    # sk: str
    last_modified: datetime = field(default_factory=datetime.utcnow)
    created_timestamp: datetime = field(default_factory=datetime.utcnow)

    def _create_key(self) -> ModelKey:
        raise NotImplementedError()

    @serialised_property
    def pk(self) -> str:
        return self._create_key()["pk"]

    @serialised_property
    def sk(self) -> str:
        return self._create_key()["sk"]

    @serialised_property
    def gsi_model_type_pk(self) -> Optional[str]:
        if self._index_model_type:
            return self.__class__.__name__
        return None

    @classmethod
    def _as_dict_value(cls, value: Any) -> Any:
        if not value or isinstance(value, type):
            return value

        if isinstance(value, list):
            return [cls._as_dict_value(val) for val in value]

        if hasattr(value, "as_dict"):
            return value.as_dict()

        if is_dataclass_instance(value):
            return asdict(value)

        return value

    def as_dict(self) -> dict[str, Any]:

        model_fields = model_properties_cache(self.__class__)  # type: ignore[arg-type]

        result: dict[str, Any] = {}

        for field_name, _, _ in model_fields:
            value = getattr(self, field_name)
            result[field_name] = self._as_dict_value(value)

        return result


class Semaphore:
    """empty class as a semaphore"""


NOTSET: Final[Semaphore] = Semaphore()
PRESERVE: Final[Semaphore] = Semaphore()

TWrapped = TypeVar("TWrapped")
TModel = TypeVar("TModel", bound=MeshModel)
TModel_co = TypeVar("TModel_co", covariant=True, bound=MeshModel)


async def maybe_log_warning(
    wrapped: Coroutine[Any, Any, Tuple[TWrapped, float, str, int]], duration_warning: float
) -> TWrapped:

    result, duration, aws_request_id, aws_retries = await wrapped
    if duration >= duration_warning or aws_retries > 0:
        add_fields(
            log_level=logging.WARN,
            duration=duration,
            aws_request_id=aws_request_id,
            aws_retries=aws_retries,
        )

    return cast(TWrapped, result)


class BaseMeshStore(BaseModelStore[TModel, ModelKey], Generic[TModel]):

    _model_uplifter: Callable[[dict[str, Any], type[TModel]], dict[str, Any]]

    def __init__(self, table_name: str):
        super().__init__(
            table_name=table_name, model_type_index_name="gsi_model_type", model_type_index_pk="gsi_model_type_pk"
        )

    @classmethod
    def _before_deserialise_model(
        cls, model_dict: dict[str, Any], model_type: type[TModel], **kwargs
    ) -> dict[str, Any]:

        uplift = kwargs.get("uplift", True)
        if not uplift:
            return model_dict

        model_dict = cls._model_uplifter(model_dict, model_type)
        return model_dict

    @classmethod
    def _serialise_field(
        cls, model: Any, field_name: str, field_type: type, metadata: Mapping[str, Any], value: Any, **kwargs
    ) -> Any:

        if field_name != "last_modified" or not isinstance(model, MeshModel):
            return super()._serialise_field(model, field_name, field_type, metadata, value, **kwargs)

        set_last_modified = kwargs.get("set_last_modified", NOTSET)
        if set_last_modified is None:
            return None

        if set_last_modified == PRESERVE:
            return cls.serialise_value(value)

        if isinstance(set_last_modified, datetime):
            value = set_last_modified
        else:
            value = datetime.utcnow()

        return cls.serialise_value(value)

    @log_action(log_level=logging.DEBUG, log_args=["key"], expected_errors=(ClientError,))
    async def get_item(self, key: ModelKey, duration_warning: float = 1, **kwargs) -> Optional[dict[str, Any]]:
        item = await maybe_log_warning(super().get_item_with_retry_info(key, **kwargs), duration_warning)
        return item

    @log_action(log_level=logging.DEBUG, log_args=["keys"], expected_errors=(ClientError,))
    async def transact_get_items(self, get_items: Sequence[TransactGetItemTypeDef]) -> list[Optional[dict]]:
        return await super().transact_get_items(get_items)

    @log_action(log_level=logging.DEBUG, log_args=["key", "model_key"], expected_errors=(ClientError,))
    async def transact_get_model(
        self, key: ModelKey, model_type: type[TBaseModel_co], **kwargs
    ) -> Optional[TBaseModel_co]:
        return await super().transact_get_model(key, model_type, **kwargs)

    @log_action(log_level=logging.DEBUG, log_args=["keys"], expected_errors=(ClientError,))
    async def transact_get_models(self, keys: Sequence[ModelKey], **kwargs) -> list[Optional[TModel]]:
        return await super().transact_get_models(keys, **kwargs)

    @log_action(log_level=logging.DEBUG, log_args=["key", "model_type"], expected_errors=(ClientError,))
    async def get_model(
        self, key: ModelKey, model_type: type[TBaseModel_co], duration_warning: float = 1, **kwargs
    ) -> Optional[TBaseModel_co]:
        model = await maybe_log_warning(super().get_model_with_retry_info(key, model_type, **kwargs), duration_warning)
        return model

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def put_item(self, item: dict[str, Any], **kwargs):
        add_fields(pk=item.get("pk"), sk=item.get("sk"))
        await super().put_item(item, **kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def put_model(self, model: TModel, **kwargs):
        add_fields(pk=model.pk, sk=model.sk, model_type=type(model))
        await super().put_model(model, **kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def put_item_if_not_exists(self, item: dict[str, Any], **kwargs) -> bool:
        add_fields(pk=item["pk"], sk=item["sk"])
        return await super().put_item_if_not_exists(item, **kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def put_model_if_not_exists(self, model: TModel, **kwargs) -> bool:
        add_fields(pk=model.pk, sk=model.sk)
        return await super().put_model_if_not_exists(model, **kwargs)

    @log_action(log_level=logging.DEBUG, log_args=["key", "consistent_read"], expected_errors=(ClientError,))
    async def item_exists(self, key: ModelKey, consistent_read: bool = False, **kwargs) -> bool:
        return await super().item_exists(key=key, consistent_read=consistent_read, **kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def delete_item(self, key: ModelKey, **kwargs):
        add_fields(pk=key.get("pk"), sk=key.get("sk"))
        await super().delete_item(key, **kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def query(self, **kwargs) -> QueryOutputTableTypeDef:
        add_fields(**kwargs)
        return await super().query(**kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def query_items(self, **kwargs) -> PagedItems[dict]:
        add_fields(**kwargs)
        return await super().query_items(**kwargs)

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def paginate(
        self, paginator_type: Literal["query", "scan", "list_backups", "list_tables"], **kwargs
    ) -> AsyncGenerator[dict, None]:
        add_fields(query_type=paginator_type, **kwargs)
        async for page in super().paginate(paginator_type, **kwargs):
            yield page

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def query_count(self, **kwargs) -> int:
        add_fields(**kwargs)
        return await super().query_count(**kwargs)

    @log_action(log_level=logging.DEBUG, log_args=["key"], expected_errors=(ClientError,))
    async def update_item(self, key: ModelKey, duration_warning: float = 1, **kwargs) -> UpdateItemOutputTableTypeDef:
        res = await maybe_log_warning(super().update_item_with_retry_info(key, **kwargs), duration_warning)
        return res

    @log_action(log_level=logging.DEBUG, expected_errors=(ClientError,))
    async def transact_write(self, actions: list[dict[str, Any]]):
        return await super().transact_write(actions)

    @log_action(log_level=logging.DEBUG, log_args=["keys", "max_concurrency"], expected_errors=(ClientError,))
    async def batch_get_item(self, keys: list[ModelKey], max_concurrency: int = 10) -> list[dict[str, Any]]:
        return await super().batch_get_item(keys, max_concurrency)
