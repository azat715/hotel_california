import enum
from typing import List, Optional

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from hotel_california.domain.models import (
    ALGORITHM,
    SECRET_KEY,
    BookingDate,
    Order,
    RefreshToken,
    Room,
    TokenResponse,
    User,
    UserLoginSchema,
    UserManager,
)
from hotel_california.service_layer.exceptions import (
    AuthenticationJwtError,
    RoomExistError,
    RoomNonFree,
)
from hotel_california.service_layer.unit_of_work import AbstractUOW


class Status(enum.IntEnum):
    ARRIVAL = 1
    DEPARTURE = 2


def add_user(user: User, workers: AbstractUOW):
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        u = manager.create(user)
        worker.data.add(u)
        worker.commit()


def login_user(data: UserLoginSchema, workers: AbstractUOW) -> TokenResponse:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        user = manager.login(data.email, data.password)
        access_token = manager.get_access_token(user.email)
        refresh_token = manager.get_refresh_token(user.email)
        token = RefreshToken(value=refresh_token)
        user.token = token
        worker.data.add(user)
        worker.commit()
        return TokenResponse(access=access_token, refresh=refresh_token)


def decode_token(token: str, audience: Optional[str] = None) -> dict:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=audience,
        )
    except ExpiredSignatureError as err:
        message = "Expiry time not valid"
        raise AuthenticationJwtError(message) from err
    except (JWTError, JWTClaimsError) as err:
        message = "Invalid jwt"
        raise AuthenticationJwtError(message) from err


def add_room(number: int, capacity: int, price: float, workers: AbstractUOW):
    """добавление комнаты"""
    with workers as worker:
        room = Room(number=number, capacity=capacity, price=price)
        if worker.data.exists(room):
            raise RoomExistError(number)
        worker.data.add(room)
        worker.commit()


def get_room_by_cap(cap: int, workers: AbstractUOW) -> List[Room]:
    """список комнат с вместимостью cap"""
    return workers.data.filter({"capacity": cap})


def get_room_by_num(room_number: int, workers: AbstractUOW) -> Optional[Room]:
    """комната по номеру"""
    return workers.data.get({"number": room_number})


def get_room_bookings_by_num(num: int, workers: AbstractUOW) -> List[BookingDate]:
    return [i.dates for i in workers.data.filter({"room_num": num})]


def check_free_room(test_dates: tuple[BookingDate], dates: List[BookingDate]):
    """проверка свободна ли комната

    Args:
        test_dates tuple): кортеж дат прибытия/убытия
        dates (List[BookingDate]): кортеж дат прибытия/убытия существующих заказов

    Raises:
        RoomNonFree: Если комната не свобода то RoomNonFree
    """

    # добавляю существующие брони
    dates.extend(test_dates)
    # сортирую по времени
    dates.sort(key=lambda x: x.date)
    # если идут два подряд заезда/выезда ошибка

    while dates:
        first = dates.pop(0)
        second = dates.pop(0)
        if second.status == first.status:
            raise RoomNonFree()


def check_free_rooms(rooms: List[Room], dates: tuple[BookingDate]) -> List[Room]:
    free_rooms = []
    for room in rooms:
        try:
            check_free_room(room, dates)
        except RoomNonFree:
            pass
        else:
            free_rooms.append(room)
    return free_rooms


def booking_room(room: Room, dates: tuple[BookingDate], workers: AbstractUOW):
    with workers as worker:
        order = Order(dates, room, booking=True)
        worker.data.add(order)
        worker.commit()
