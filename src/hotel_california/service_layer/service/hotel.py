from datetime import date
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
    UserManager, RoomManager, Status, OrderManager,
)
from hotel_california.service_layer.exceptions import (
    AuthenticationJwtError,
    UserNotAdmin, OrderNotCancel,
)
from hotel_california.service_layer.unit_of_work import UOW


def add_user(name: str, email: str, password: str, is_admin: bool, workers: UOW):
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        u = manager.create(name, email, password, is_admin)
        worker.data.add(u)
        worker.commit()


def get_user_by_email(email: str, workers: UOW):
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        return manager.get_user_by_email(email)


def login_user_and_get_tokens(email: str, password: str, workers: UOW) -> Tuple[str, str]:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        user = manager.login(email, password)
        access = manager.get_access_token(email)
        refresh = manager.get_refresh_token(email)
        user.token = RefreshToken(value=refresh)
        worker.data.add(user)
        worker.commit()
        return access, refresh


def get_access_token(email: str, password: str, workers: UOW) -> Tuple[str, str]:
    with workers as worker:
        manager = UserManager.init(worker.data.all())
        manager.login(email, password)
        return manager.get_access_token(email)


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


def add_room(number: int, capacity: int, price: float, workers: UOW) -> Room:
    """добавление комнаты"""
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        room = manager.create(number, capacity, price)
        worker.data.add(room)
        worker.commit()
        return room.number


def get_order_by_id(order_id: int, workers: UOW) -> Order:
    with workers as worker:
        manager = OrderManager.init(worker.data.all())
        order = manager.get_order_by_id(order_id)
        return order.get_dict


def find_rooms(cap: int, arrival: str, departure: str, workers: UOW) -> List[Room]:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        dates = (BookingDate.parse_str(arrival, Status.ARRIVAL), BookingDate.parse_str(departure, Status.DEPARTURE))
        return manager.find_room(dates, cap)


def get_room_by_num(num: int, workers: UOW) -> Room:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        return manager.get_room_by_num(num)


def get_rooms(workers: UOW) -> List[Room]:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        return manager.rooms.values()


def get_room_orders(num: int, workers: UOW) -> List[dict]:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        room = manager.get_room_by_num(num)
        res = []
        for order in room.orders:
            res.append(order.get_dict)
        return res


def check_room(num: int, arrival: date, departure: date, workers: UOW) -> Room:
    with workers as worker:
        manager = RoomManager.init(worker.data.all())
        dates = (BookingDate.parse_str(arrival, Status.ARRIVAL), BookingDate.parse_str(departure, Status.DEPARTURE))
        return manager.check_room(num, dates)


def create_order(arrival: date, departure: date, workers: UOW):
    with workers as worker:
        manager = OrderManager.init(worker.data.all())
        dates = (BookingDate.parse_str(arrival, Status.ARRIVAL), BookingDate.parse_str(departure, Status.DEPARTURE))
        order = manager.create(dates)
        return order


def delete_order(order_id, workers: UOW):
    with workers as worker:
        manager = OrderManager.init(worker.data.all())
        order = manager.get_order_by_id(order_id)
        if manager.check_can_delete(order):
            worker.data.delete(order)
        else:
            message = "Бронь можно отменить только за три дня до заезда"
            raise OrderNotCancel(message)
        worker.commit()
