"""Handle all user related API."""
from typing import List
import uuid

from fastapi import APIRouter, Body
from odmantic import ObjectId
from sqlmodel import Session, select

from dice_be.exceptions import IDNotFound
from dice_be.models.users import NUser

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)


# pylint:disable=redefined-builtin, invalid-name
async def get_user_by_id(id: uuid.UUID) -> NUser:
    """Retrieve a user by their ID from the DB
    :param id: ID of the user to get
    :return: Always returns a user, or raises an exception
    :raise: IDNotFound.
    """
    if user := await NUser.find_one(NUser.id == id):
        return user
    raise IDNotFound(NUser, id)


@router.get('/', response_model=list[NUser])
async def get_all_users():
    """Retrieve a list of all users."""
    return NUser.find_all().to_list()


@router.post('/', response_model=NUser)
async def create_user(name: str = Body(..., embed=True)):
    """Create a single user with a given name."""
    return await NUser(name=name).create()


# pylint:disable=redefined-builtin, invalid-name
@router.get(
    '/{id}/',
    response_model=NUser,
    responses=IDNotFound.response(),
    name='Get User by ID',
)
async def get_user_by_id_endpoint(id: uuid.UUID):
    """Retrieve a single user by their ID."""
    return await get_user_by_id(id)


# pylint:disable=redefined-builtin, invalid-name
@router.post('/{id}/friends/', response_model=NUser, responses=IDNotFound.response())
async def add_friends(id: uuid.UUID, friends: List[uuid.UUID] = Body(..., embed=True)):
    """Add a multiple friends to a single user by their IDs."""
    raise NotImplementedError
