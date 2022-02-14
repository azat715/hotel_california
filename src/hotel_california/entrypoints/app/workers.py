from hotel_california.adapters.repository import UserRepository, RoomRepository, OrderRepository
from hotel_california.service_layer.unit_of_work import (
    DEFAULT_SESSION_FACTORY,
    SqlAlchemyUOW,
)


def get_user_worker():
    return SqlAlchemyUOW(repo=UserRepository, session_factory=DEFAULT_SESSION_FACTORY)


def get_room_worker():
    return SqlAlchemyUOW(repo=RoomRepository, session_factory=DEFAULT_SESSION_FACTORY)


def get_order_worker():
    return SqlAlchemyUOW(repo=OrderRepository, session_factory=DEFAULT_SESSION_FACTORY)
