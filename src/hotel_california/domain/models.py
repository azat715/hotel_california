import enum
from abc import ABC
from dataclasses import field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr  # pylint: disable=no-name-in-module
from pydantic import validator
from pydantic.dataclasses import dataclass

from hotel_california.config import get_settings
from hotel_california.service_layer.exceptions import (
    InvalidPassword,
    NonUniqEmail,
    NotFoundEmail,
    UserNotAdmin,
    RoomExistError,
    RoomNonFree
)

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


@dataclass(unsafe_hash=True)
class TokenResponse(Model):
    access: str
    refresh: str


@dataclass(unsafe_hash=True)
class UserLoginSchema(Model):
    """логин пользователя"""

    email: EmailStr
    password: str


@dataclass(unsafe_hash=True)
class RoomFindSchema(Model):
    """форма для поиска комнаты"""
    capacity: int
    arrival: datetime
    departure: datetime


class Status(enum.IntEnum):
    ARRIVAL = 1
    DEPARTURE = 2


@dataclass(unsafe_hash=True)
class BookingDate(Model):
    date: date
    status: Status  # ARRIVAL/DEPARTURE

    @classmethod
    def parse_str(cls, value: str, status: Status):
        """парсинг даты

        Args:
            value: дата в ISO формате YYYY-MM-DD
            status: Status enum - ARRIVAL/DEPARTURE

        Raises:
            ValueError - Invalid isoformat string

        Returns:
            BookingDate
        """
        return cls(date=date.fromisoformat(value), status=status)


@dataclass(unsafe_hash=True)
class Order(Model):
    guest: str
    # даты желаемого заезда и выезда
    dates: List[BookingDate] = field(default_factory=list)

    def __post_init__(self):
        assert len(self.dates) == 2, "Две даты в ордере"


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
    email: EmailStr  # должно быть уникальным
    password: str  # hash пароля
    token: Optional[RefreshToken] = None
    is_admin: bool = False

    @validator("password", pre=True, always=True)
    def len_password_(cls, v):  # pylint: disable=no-self-argument
        if len(v) < 8:
            raise ValueError("Длина пароля меньше 8 символов")
        return v


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

    def create(self, user: User) -> User:
        self._validate(user.email)
        user.password = self._hash_password(user.password)
        return user

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

    def _get_access_token(self, email: str) -> str:
        return self._get_token(email, expires_delta=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    def _get_refresh_token(self, email: str) -> str:
        return self._get_token(
            email,
            expires_delta=self.REFRESH_TOKEN_EXPIRE_MINUTES,
            audience=self.AUDIENCE,
        )

    def get_tokens(self, email: str) -> TokenResponse:
        access = self._get_access_token(email)
        refresh = self._get_refresh_token(email)
        return TokenResponse(access=access, refresh=refresh)

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

    def _validate(self, number: int) -> bool:
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
        res.extend(i.dates for i in room.orders)
        # сортирую по времени
        res.sort(key=lambda x: x.date)
        # если идут два подряд заезда/выезда ошибка
        while res:
            first = res.pop(0)
            second = res.pop(0)
            if second.status == first.status:
                return False
        return True

    def create(self, room: Room) -> Room:
        self._validate(room.number)
        return room

    def find_room(self, dates: Tuple[BookingDate, BookingDate], cap: int) -> List[Room]:
        rooms = [i for i in self.rooms.values() if i.capacity == cap]
        res = []
        for room in rooms:
            if self._check_free_room(dates, room):
                res.append(room)
        return res
        
        # Поиск номера (указываем даты и количество мест, возвращаем список (номер, вместительность, цена)

    @classmethod
    def init(cls, rooms: List[Room]) -> "RoomManager":
        res = {}
        for room in [i[0] for i in rooms]:
            res[room.number] = room
        return cls(res)
