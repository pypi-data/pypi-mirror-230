from typing import Generator

import pytest
from mypy_boto3_dynamodb.service_resource import Table
from nhs_aws_helpers.fixtures import temp_dynamodb_table


@pytest.fixture(scope="session")
def session_temp_mesh_table() -> Generator[Table, None, None]:
    yield from temp_dynamodb_table("local-mesh")


@pytest.fixture(scope="function")
def temp_mesh_table(session_temp_mesh_table) -> Generator[Table, None, None]:  # pylint: disable=redefined-outer-name
    table = session_temp_mesh_table
    result = table.scan(ProjectionExpression="pk, sk", ConsistentRead=True)
    with table.batch_writer(["pk", "sk"]) as writer:
        while True:
            items = result.get("Items", [])
            if not items:
                break
            for item in items:
                writer.delete_item(dict(pk=item["pk"], sk=item["sk"]))
            if len(writer._items_buffer) > 0:  # pylint: disable=protected-access
                writer._flush()  # pylint: disable=protected-access
            if not result.get("LastEvaluatedKey"):
                break
            result = session_temp_mesh_table.scan(
                ProjectionExpression="pk, sk", ConsistentRead=True, ExclusiveStartKey=result.get("LastEvaluatedKey")
            )

    yield table
