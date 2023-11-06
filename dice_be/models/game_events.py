from enum import Enum
from typing import List, Literal, Union, Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from dice_be.models.games import Dice, GameData, GameRules, PlayerData


class PlayerReady(BaseModel):
    """Signals to the server that the player is ready
    Broadcast from server.
    """

    event: Literal['player_ready'] = 'player_ready'
    ready: bool = True
    left_player_id: UUID | None = None
    right_player_id: UUID | None = None


class ReadyConfirm(BaseModel):
    event: Literal['ready_confirm'] = 'ready_confirm'
    success: bool
    error: str | None = None


class PlayerLeave(BaseModel):
    """Signals to the server that the player is leaving."""

    event: Literal['player_leave']


class GameStart(BaseModel):
    event: Literal['game_start'] = 'game_start'
    rules: GameRules


class RoundStart(BaseModel):
    event: Literal['round_start'] = 'round_start'
    dice: List[Dice]

    @classmethod
    def from_player(cls, player: PlayerData):
        return cls(dice=player.dice)


class AccusationType(str, Enum):
    Standard = 'standard'
    Exact = 'exact'
    Paso = 'paso'


class Accusation(BaseModel):
    event: Literal['accusation']
    type: AccusationType
    accused_player: UUID
    dice_value: int | None = None
    dice_count: int | None = None


class RoundEnd(BaseModel):
    event: Literal['round_end'] = 'round_end'
    winner: UUID
    loser: UUID
    correct_accusation: bool
    accusation_type: AccusationType
    dice_value: int | None = None
    dice_count: int | None = None
    joker_count: int = None
    players: str

    @classmethod
    def from_context(
        cls,
        accusation: Accusation,
        correct_accusation: bool,
        dice_count: int,
        joker_count: int,
        game_data: GameData,
        winner: PlayerData,
        loser: PlayerData,
    ):
        return cls(
            winner=winner.id,
            loser=loser.id,
            correct_accusation=correct_accusation,
            accusation_type=accusation.type,
            dice_value=accusation.dice_value,
            dice_count=dice_count,
            joker_count=joker_count,
            players=game_data.players_dice(),
        )


class Event(BaseModel):
    __root__: Annotated[Union[PlayerReady, PlayerLeave, Accusation], Field(
        ...,
        discriminator='event',
    )]
