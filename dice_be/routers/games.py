"""Handle all game related API."""

from typing import TYPE_CHECKING

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Body, WebSocket, WebSocketException, status
from starlette.websockets import WebSocketDisconnect
from loguru import logger
from uuid import UUID

from dice_be.managers.playground import playground
from dice_be.exceptions import GameNotFound
from dice_be.models.games import Code, GameData, GameProgression, GameRules
from dice_be.routers.users import get_user_by_id

if TYPE_CHECKING:
    from dice_be.managers.games import GameManager
    from dice_be.models.users import User

router = APIRouter(
    prefix='/games',
    tags=['Games'],
)


@router.post('/', response_model=Code)
async def create_game(game_rules: GameRules = Body(..., embed=True)):
    """Creates a new game."""
    return playground.create_game(game_rules)


@router.get('/{code}/', response_model=GameData, responses=GameNotFound.response())
async def get_game(code: str):
    """Gets all the info about a game."""
    return playground.get_game(code).game_data


@router.get(
    '/{code}/state',
    response_model=GameProgression,
    responses=GameNotFound.response(),
)
async def get_game_state(code: str):
    """Gets the state of a game, use this before attempting to join."""
    return playground.get_game(code).game_data.progression


@router.get('/{code}/{user_id}', response_model=bool, responses=GameNotFound.response())
async def check_player_in_game(code: str, user_id: str):
    """Checks if the player is in the game."""
    return ObjectId(user_id) in playground.get_game(code).player_mapping


@router.websocket('/{code}/ws/')
async def websocket_endpoint(code: Code, websocket: WebSocket):
    """API to join a game.

    :param code: Code of the game the client wants to join
    :param websocket: The websocket that the client is connecting on
    """
    await websocket.accept()

    try:
        user_id = UUID((await websocket.receive_json())['id'])
    except ValueError as e:
        raise WebSocketException(code=status.WS_1002_PROTOCOL_ERROR, reason=str(e))

    try:
        user: User = await get_user_by_id(user_id)
    except InvalidId as e:
        raise WebSocketException(code=status.WS_1002_PROTOCOL_ERROR, reason=str(e))

    game: GameManager = playground.get_game(code)

    await game.handle_connect(user, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                await game.handle_json(user, data)
            except TypeError as e:
                raise WebSocketException(code=status.WS_1002_PROTOCOL_ERROR, reason=str(e))
    except WebSocketDisconnect:
        # Client disconnected
        await game.handle_disconnect(user)
