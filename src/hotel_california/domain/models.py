import enum
from abc import ABC
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from email_validator import EmailNotValidError, validate_email
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from hotel_california.config import get_settings
from hotel_california.service_layer.exceptions import (
    InvalidPassword,
    NonUniqEmail,
    NotFoundEmail,
    RoomExistError,
    RoomNonFree,
    UserNotAdmin, RoomNotFound, DatesNotValid, OrderNotFound,
)

# from pydantic.dataclasses import dataclass # pydantic dataclasses неправильно мапятся алхимией при relationship один к многим -AttributeError: 'list' object has no attribute '_sa_adapter


settings = get_settings()

APP_NAME = settings.APP_NAME
AUDIENCE = "/users/token/refresh/"
LOGIN_URL = "users/login"
SECRET_KEY = settings.AUTH.SECRET_KEY
ALGORITHM = settings.AUTH.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.AUTH.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = 4320  # время действия 3 дня


class Model(ABC):
    pass


class Status(enum.IntEnum):
    ARRIVAL = 1
    DEPARTURE = 2


@dataclass(unsafe_hash=True)
class BookingDate(Model):
    date: date
    status: Status  # ARRIVAL/DEPARTURE

    @classmethod
    def parse_str(cls, value: date, status: Status):
        """парсинг даты

        Args:
            value: дата в ISO формате YYYY-MM-DD
            status: Status enum - ARRIVAL/DEPARTURE

        Raises:
            ValueError - Invalid isoformat string

        Returns:
            BookingDate
        """
        return cls(date=value, status=status)


@dataclass(unsafe_hash=True)
class Order(Model):
    identity: int
    # даты желаемого заезда и выезда
    dates: List[BookingDate] = field(default_factory=list)

    def __post_init__(self):

        assert len(self.dates) == 2, "Две даты в ордере"

    @property
    def get_dict(self) -> dict:  # из-за того что я даты прибытия убытия храню списком очень сложное получение
        res = {}
        for i in self.dates:
            if i.status == Status.ARRIVAL:
                res["arrival"] = i.date
            elif i.status == Status.DEPARTURE:
                res["departure"] = i.date
        res["identity"] = self.identity
        return res


@dataclass(unsafe_hash=True)
class Room(Model):
    """комната"""

    number: int  # номер комнаты, уникальный
    capacity: int
    price: float
    orders: List[Order] = field(default_factory=list)

    def __post_init__(self):
        assert self.capacity > 0, "Bместительность capacity должно быть больше нуля"
        assert self.price > 0, "Цена price должна быть больше нуля"


@dataclass(unsafe_hash=True)
class RefreshToken(Model):
    value: str


@dataclass(unsafe_hash=True)
class User(Model):
    name: str
    email: str  # должно быть уникальным
    password: str  # hash пароля
    is_admin: bool = False
    token: Optional[RefreshToken] = None

    def __post_init__(self):
        if len(self.password) < 8:
            raise ValueError("Длина пароля меньше 8 символов")
        try:
            valid = validate_email(self.email)
            self.email = valid.email
        except EmailNotValidError as err:
            raise err


PasswordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:
    """что то типа агрегата чтоли"""

    APP_NAME = APP_NAME
    AUDIENCE = AUDIENCE
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_MINUTES = REFRESH_TOKEN_EXPIRE_MINUTES  # время действия 3 дня

    def __init__(self, users: Dict[str, User]) -> None:
        self.users = users

    def _validate(self, email: str) -> bool:
        if email in self.users:
            raise NonUniqEmail(email)

    def exists(self, email: str):
        try:
            return self.users[email]
        except KeyError as err:
            raise NotFoundEmail(email) from err

    def _hash_password(self, password: str) -> str:
        return PasswordContext.hash(password)

    def check_admin(self, email: str) -> bool:
        user = self.exists(email)
        if user.is_admin:
            return True
        raise UserNotAdmin(email)

    def _check_credentials(self, password_raw: str, password: str):
        if not PasswordContext.verify(password_raw, password):
            return False
        return True

    def create(self, name: str, email: str, password: str, is_admin: bool = False) -> User:
        self._validate(email)
        password = self._hash_password(password)
        return User(name, email, password, is_admin)

    def login(self, email: str, password: str) -> User:
        u = self.exists(email=email)
        if not self._check_credentials(password, u.password):
            raise InvalidPassword(email=email)
        return u

    def _get_token(
            self, email: str, expires_delta: int, audience: Optional[str] = None
    ) -> str:
        payload = {
            "iss": self.APP_NAME,
            "sub": email,
            "exp": datetime.utcnow() + timedelta(minutes=expires_delta),
        }
        if audience:
            payload["aud"] = audience
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_access_token(self, email: str, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
        return self._get_token(email, expires_delta=expires_delta)

    def get_refresh_token(self, email: str) -> str:
        return self._get_token(
            email,
            expires_delta=self.REFRESH_TOKEN_EXPIRE_MINUTES,
            audience=self.AUDIENCE,
        )

    def get_user_by_email(self, email: str) -> User:
        self.exists(email=email)
        return self.users[email]

    @classmethod
    def init(cls, users: List[User]) -> "UserManager":
        res = {}
        for user in [i[0] for i in users]:
            res[user.email] = user
        return cls(res)


class RoomManager:
    """что то типа агрегата чтоли"""

    def __init__(self, rooms: Dict[int, Room]) -> None:
        self.rooms = rooms

    def _validate(self, number: int):
        if number in self.rooms:
            raise RoomExistError(number)

    @staticmethod
    def _check_free_room(dates: Tuple[BookingDate, BookingDate], room: Room) -> bool:
        """проверка свободна ли комната

        Args:
            test_dates tuple): кортеж дат прибытия/убытия
            room: комната

        Return:
            True - свободна
            False - занята

        Raises:
            RoomNonFree: Если комната не свободна то RoomNonFree
        """
        res = []
        res.extend(dates)
        # добавляю существующие брони
        for i in room.orders:
            res.extend(i.dates)
        # res.extend([i.dates for i in room.orders])
        # сортирую по времени
        res = sorted(res, key=lambda x: x.date)
        # если идут два подряд заезда/выезда ошибка
        while res:
            first = res.pop(0)
            second = res.pop(0)
            if second.status == first.status:
                return False
        return True

    def create(self, number: int, capacity: int, price: float) -> Room:
        self._validate(number)
        return Room(number, capacity, price)

    def find_room(self, dates: Tuple[BookingDate, BookingDate], cap: int) -> List[Room]:
        rooms = [i for i in self.rooms.values() if i.capacity == cap]
        res = []
        for room in rooms:
            if self._check_free_room(dates, room):
                res.append(room)
        return res

    def get_room_by_num(self, num: int):
        try:
            return self.rooms[num]
        except KeyError as err:
            raise RoomNotFound(num) from err

        # Поиск номера (указываем даты и количество мест, возвращаем список (номер, вместительность, цена)

    def check_room(self, num: int, dates: Tuple[BookingDate, BookingDate]) -> int:
        room = self.get_room_by_num(num)
        if not self._check_free_room(dates, room):
            raise RoomNonFree(num)
        return room

    @classmethod
    def init(cls, rooms: List[Room]) -> "RoomManager":
        res = {}
        for room in [i[0] for i in rooms]:
            res[room.number] = room
        return cls(res)


class OrderManager:
    def __init__(self, orders: Dict[int, Order]):
        self.orders = orders

    def get_id(self) -> int:
        """чтото типа автоинкремента pk"""
        if self.orders:
            return max(self.orders.keys()) + 1

        return 1

    @classmethod
    def init(cls, orders: List[Order]) -> "OrderManager":
        res = {}
        for order in [i[0] for i in orders]:
            res[order.identity] = order
        return cls(res)

    def create(self, dates: Tuple[BookingDate, BookingDate]) -> Order:
        arrival, departure = dates
        if arrival.date > departure.date:
            message = "Дата прибытия позже чем дата убытия"
            raise DatesNotValid(message)
        order_id = self.get_id()
        return Order(
            identity=order_id,
            dates=list(dates)
        )

    def get_order_by_id(self, order_id: int) -> Order:
        try:
            return self.orders[order_id]
        except KeyError as err:
            raise OrderNotFound(order_id) from err

    @staticmethod
    def check_can_delete(order: Order) -> bool:
        today = date.today()
        for i in order.dates:
            if i.status == Status.ARRIVAL:
                if (i.date - today) > timedelta(days=3):
                    return True
        return False
