"""Handle all user related API."""
from typing import List

from fastapi import APIRouter, Body
from odmantic import ObjectId
from sqlmodel import Session, select

from dice_be.dependencies import engine as db
from dice_be.exceptions import IDNotFound
from dice_be.models.users import NUser, User

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)


# pylint:disable=redefined-builtin, invalid-name
async def get_user_by_id(id: ObjectId) -> NUser:
    """Retrieve a user by their ID from the DB
    :param id: ID of the user to get
    :return: Always returns a user, or raises an exception
    :raise: IDNotFound.
    """
    if user := await db.find_one(User, User.id == id):
        return user
    raise IDNotFound(User, id)


@router.get('/', response_model=list[NUser])
async def get_all_users():
    """Retrieve a list of all users."""
    with Session(db) as session:
        return session.exec(select(NUser)).all()


@router.post('/', response_model=NUser)
async def create_user(name: str = Body(..., embed=True)):
    """Create a single user with a given name."""
    with Session(db) as session:
        new_user = NUser(name=name)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    # return await db.save(User(name=name))


# pylint:disable=redefined-builtin, invalid-name
@router.get(
    '/{id}/',
    response_model=User,
    responses=IDNotFound.response(),
    name='Get User by ID',
)
async def get_user_by_id_endpoint(id: ObjectId):
    """Retrieve a single user by their ID."""
    return await get_user_by_id(id)


# pylint:disable=redefined-builtin, invalid-name
@router.post('/{id}/friends/', response_model=User, responses=IDNotFound.response())
async def add_friends(id: ObjectId, friends: List[ObjectId] = Body(..., embed=True)):
    """Add a multiple friends to a single user by their IDs."""
    user = await get_user_by_id(id)
    user.friend_ids.extend(friends)
    await db.save(user)
    return user
