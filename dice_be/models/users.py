"""Models for users data."""

from uuid import UUID, uuid4

from pydantic import Field
from beanie import Document


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    friends: list[UUID] = []

