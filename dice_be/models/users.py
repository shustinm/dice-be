"""Models for users data."""

from typing import List
from uuid import UUID, uuid4

from odmantic import Model, ObjectId
from pydantic import Field
from beanie import Document


# pylint: disable=abstract-method
class User(Model):
    """User data, this class defines how users are saved in the DB."""

    name: str
    friend_ids: List[ObjectId] = []


class NUser(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    friends: list[UUID] = []

