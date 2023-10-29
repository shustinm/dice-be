import pytest
from mongomock_motor import AsyncMongoMockClient

from dice_be.models.users import NUser


pytestmark = pytest.mark.anyio


async def test_mock_client(mock_client: AsyncMongoMockClient):
    collection = mock_client['tests']['test-1']

    assert await collection.find({}).to_list() == []

    result = await collection.insert_one({'a': 1})
    assert result.inserted_id

    assert len(await collection.find({}).to_list()) == 1


async def test_engine():
    user = await NUser(name='hello').create()
    assert user.name == 'hello'
    assert await NUser.find_all().to_list() == [user]

