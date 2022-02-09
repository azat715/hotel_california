from hotel_california.adapters.repository import UserRepository, RoomRepository
from hotel_california.service_layer.unit_of_work import (
    DEFAULT_SESSION_FACTORY,
    SqlAlchemyUOW,
)


def user_worker():
    return SqlAlchemyUOW(repo=UserRepository, session_factory=DEFAULT_SESSION_FACTORY)


def room_worker():
    return SqlAlchemyUOW(repo=RoomRepository, session_factory=DEFAULT_SESSION_FACTORY)