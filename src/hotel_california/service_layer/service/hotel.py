import enum
from typing import List, Optional, Tuple

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from hotel_california.domain.models import (
    ALGORITHM,
    SECRET_KEY,
    BookingDate,
    Order,
    RefreshToken,
    Room,
    User,
    UserManager, RoomManager, Status,
)
from hotel_california.service_layer.exceptions import (
    AuthenticationJwtError,
    RoomExistError,
    RoomNonFree,
    UserNotAdmin,
)
from hotel_california.service_layer.unit_of_work import UOW


def add_user(name: str, email: str, password: str, is_admin: bool, workers: UOW):
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        u = manager.create(name, email, password, is_admin)
        worker.data.add(u)
        worker.commit()


def login_user(email: str, password: str, workers: UOW) -> Tuple[str, str]:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        user = manager.login(email, password)
        access = manager.get_access_token(email)
        refresh = manager.get_refresh_token(email)
        user.token = RefreshToken(value=refresh)
        worker.data.add(user)
        worker.commit()
        return access, refresh


# def get_tokens(email: str, workers: AbstractUOW) -> TokenResponse:
#     with workers as worker:
#         manager = UserManager.init(worker.data.all())
#         user = manager.get_user_by_email(email)
#         token = manager.get_tokens(user.email)
#         user.token = RefreshToken(value=token.refresh)
#         worker.data.add(user)
#         worker.commit()


def check_is_admin(email: str, workers: UOW) -> bool:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        user = manager.get_user_by_email(email)
        if not user.is_admin:
            raise UserNotAdmin(email=email)


def refresh_token(email: str, workers: UOW) -> Tuple[str, str]:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        user = manager.get_user_by_email(email)
        if not user.token:
            message = "Refresh token alredy used"
            raise AuthenticationJwtError(message)
        access = manager.get_access_token(user.email)
        refresh = manager.get_refresh_token(user.email)
        user.token = RefreshToken(value=refresh)
        worker.data.add(user)
        worker.commit()
        return access, refresh


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


def add_room(room: Room, workers: UOW) -> None:
    """добавление комнаты"""
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        u = manager.create(room)
        worker.data.add(u)
        worker.commit()


# def get_room_by_cap(cap: int, workers: UOW) -> List[Room]:
#     """список комнат с вместимостью cap"""
#     return workers.data.filter({"capacity": cap})
#
#
# def get_room_by_num(room_number: int, workers: UOW) -> Optional[Room]:
#     """комната по номеру"""
#     return workers.data.get({"number": room_number})
#
#
# def get_room_bookings_by_num(num: int, workers: UOW) -> List[BookingDate]:
#     return [i.dates for i in workers.data.filter({"room_num": num})]

def find_room(cap: int, arrival: str, departure: str, workers: UOW) -> List[Room]:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        dates = (BookingDate.parse_str(arrival, Status.ARRIVAL), BookingDate.parse_str(departure, Status.DEPARTURE))
        return manager.find_room(dates, cap)


# def check_free_rooms(rooms: List[Room], dates: tuple[BookingDate]) -> List[Room]:
#     free_rooms = []
#     for room in rooms:
#         try:
#             check_free_room(room, dates)
#         except RoomNonFree:
#             pass
#         else:
#             free_rooms.append(room)
#     return free_rooms


def booking_room(room: Room, dates: tuple[BookingDate], workers: UOW):
    with workers as worker:
        order = Order(dates, room, booking=True)
        worker.data.add(order)
        worker.commit()
