"""Handle all user related API."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Body
from odmantic import ObjectId
from sqlmodel import Session, select

from dice_be.exceptions import IDNotFound
from dice_be.models.users import User

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)


# pylint:disable=redefined-builtin, invalid-name
async def get_user_by_id(id: UUID) -> User:
    """Retrieve a user by their ID from the DB
    :param id: ID of the user to get
    :return: Always returns a user, or raises an exception
    :raise: IDNotFound.
    """
    if user := await User.find_one(User.id == id):
        return user
    raise IDNotFound(User, id)


@router.get('/', response_model_by_alias=True)
async def get_all_users() -> list[User]:
    """Retrieve a list of all users."""
    return await User.find_all().to_list()


@router.post('/', response_model_by_alias=True)
async def create_user(name: str = Body(..., embed=True)) -> User:
    """Create a single user with a given name."""
    return await User(name=name).create()


# pylint:disable=redefined-builtin, invalid-name
@router.get(
    '/{id}/',
    responses=IDNotFound.response(),
    name='Get User by ID',
    response_model_by_alias=True
)
async def get_user_by_id_endpoint(id: UUID) -> User:
    """Retrieve a single user by their ID."""
    return await get_user_by_id(id)


# pylint:disable=redefined-builtin, invalid-name
@router.post('/{id}/friends/', responses=IDNotFound.response(), response_model_by_alias=True)
async def add_friends(id: UUID, friends: List[UUID] = Body(..., embed=True)) -> User:
    """Add a multiple friends to a single user by their IDs."""
    raise NotImplementedError
