import pytest
from typing import Callable
from uuid import UUID
from contextlib import ExitStack

from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from dice_be.__main__ import app
from dice_be.models.games import Code, GameRules, GameData, GameProgression
from dice_be.models.users import User
from dice_be.models.game_events import PlayerReady

pytestmark = pytest.mark.anyio

@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def game(http_client: TestClient) -> GameData:
    raw_code = http_client.post('/games/', json={'game_rules': dict(GameRules())})
    game_code = Code(raw_code.json())
    game_info = http_client.get(f'/games/{game_code}')

    return GameData(**game_info.json())


@pytest.fixture
def players(create_user: Callable[[str], User], game: GameData, http_client: TestClient) -> list[tuple[User, WebSocketTestSession]]:
    with ExitStack() as stack:
        connections = []
        for num in range(5):
            user = create_user(f'player{num}')
            ws = http_client.websocket_connect(f'/games/{game.code}/ws/')
            stack.enter_context(ws)
            connections.append((user, ws))

            # Provide the player ID to join the game room
            ws.send_json({'id': str(user.id)})

        yield connections  # pyright: ignore

@pytest.fixture
def create_user(http_client) -> Callable[[str], User]:
    def _(username):
        res = http_client.post('/users/', json={'name': username})
        return User(**res.json())

    return _


def test_game_creation(game: GameData):
    assert game.event == 'game_update'
    assert len(game.code) == 4 and game.code.isnumeric()
    assert game.progression == GameProgression.LOBBY == 'lobby'


def test_user_creation(create_user: Callable[[str], User], http_client: TestClient):
    user1 = create_user('Shustak')
    user = http_client.get(f'/users/{user1.id}').json()
    assert UUID(user['_id']) == user1.id
    assert user['name'] == user1.name == 'Shustak'


async def start_game(game: GameData, players: list[tuple[User, WebSocketTestSession]]):
    for _, ws in players:
        ws.send_json(PlayerReady().dict())
        ws.receive_json()


async def test_game_start(game: GameData, players: list[tuple[User, WebSocketTestSession]]):
    await start_game(game, players)

