"""Models for users data."""

from typing import List

from odmantic import Model, ObjectId
from sqlmodel import Field, SQLModel

from dice_be.dependencies import engine

# pylint: disable=abstract-method
class User(Model):
    """User data, this class defines how users are saved in the DB."""

    name: str
    friend_ids: List[ObjectId] = []


class NUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

