import pytest

from fastapi import WebSocket
from fastapi.testclient import TestClient

from dice_be.__main__ import app
from dice_be.models.games import GameRules, GameData, GameProgression
from dice_be.models.users import User
from dice_be.dependencies import Code

@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def game(http_client: TestClient):
    raw_code = http_client.post('/games/', json={'game_rules': dict(GameRules())})
    game_code = Code(raw_code.json())
    game_info = http_client.get(f'/games/{game_code}')
    return GameData(**game_info.json())


@pytest.fixture
def user1(http_client):
    res = http_client.post('/users/', json={'name': 'Shustak'})
    user = User(**res.json())

@pytest.fixture
def player1(http_client: TestClient, game: GameData, user1):
    print(user1)
    # with http_client.websocket_connect(f'/games/{game.code}/ws/') as ws:
    #     ws.send_json({'id': 'test'})
        # yield ws.receive_json()

def test_game_creation(game: GameData):
    assert game.event == 'game_update'
    assert len(game.code) == 4 and game.code.isnumeric()
    assert game.progression == GameProgression.LOBBY == 'lobby'


def test_user_creation(user1):
    print(user1)

