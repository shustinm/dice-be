import pytest

from mongomock_motor import AsyncMongoMockClient

from dice_be.models.users import NUser
from beanie import init_beanie

pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def mock_client():
    yield AsyncMongoMockClient()

@pytest.fixture(autouse=True)
async def engine(mock_client):
    yield await init_beanie(database=mock_client.db_name, document_models=[NUser])  # pyright: ignore
