"""Models for games and game metadata."""
import random
from collections import Counter
from enum import Enum
from typing import List, Literal, TypeAlias, Annotated

from bson import ObjectId
from uuid import UUID, uuid4
from pydantic import Field, NonNegativeInt, conint, BaseModel

from dice_be.models.users import User, NUser
from dice_be.models.utils import OID, MongoModel

Code: TypeAlias = str
Dice = Annotated[int, Field(ge=1, le=6)]

JOKER_DICE = 1


# pylint: disable=abstract-method
class GameProgression(str, Enum):
    """Represents the current state of the game."""

    LOBBY = 'lobby'
    IN_GAME = 'in_game'


class PlayerData(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = ""
    dice: List[Dice] = []
    current_dice_count: NonNegativeInt = 0
    ready: bool = False
    left_player_id: UUID  | None = None
    right_player_id: UUID | None = None

    def roll_dice(self) -> 'PlayerData':
        self.dice = [random.randint(1, 6) for _ in range(self.current_dice_count)]
        return self

    def is_paso(self) -> bool:
        if len(self.dice) != 5:
            return False

        dice_set = set(self.dice)
        if len(dice_set) == 4:
            return True

        if len(dice_set) == 2:
            ((_, most_common_count),) = Counter(self.dice).most_common(1)
            if most_common_count == 4:
                return True

        return False


class GameRules(MongoModel):
    initial_dice_count: int = 5
    paso_allowed: bool = True
    exact_allowed: bool = True


class GameData(MongoModel):
    """Data of an active game."""

    event: Literal['game_update']
    code: Code
    progression: GameProgression = GameProgression.LOBBY
    rules: GameRules = GameRules()
    players: list[PlayerData] = []

    def add_player(self, player: NUser):
        self.players.append(player := PlayerData(id=player.id, name=player.name))
        return player

    def remove_player(self, player: User):
        for p in self.players:
            if player.id == p.id:
                # It's probably ok to remove values while iterating over the list because we return right after
                return self.players.remove(p)
        return None

    def lobby_json(self, *data_filter) -> str:
        includes = {'event', 'progression', 'rules', 'players'}

        if not data_filter:
            return self.json(include=includes)

        return self.json(include=includes & (set(data_filter) | {'event'}))

    def player_update_json(self) -> str:
        return self.json(
            include={'event': True, 'players': {'__all__': {'id', 'name', 'ready'}}},
        )

    def start_game_json(self) -> str:
        return self.json(include={'event': True, 'rules': True})

    def round_start_json(self) -> str:
        return self.json(
            include={
                'event': True,
                'players': {'__all__': {'id', 'name', 'current_dice_count'}},
            },
        )

    def players_dice(self) -> str:
        return self.json(include={'players': {'__all__': {'id', 'name', 'dice'}}})
