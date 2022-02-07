from abc import ABC
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

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
class Room(Model):
    """комната"""

    number: int  # номер комнаты, уникальный
    capacity: int
    price: float

    def __post_init__(self):
        assert self.capacity > 0, "Bместительность capacity должно быть больше нуля"
        assert self.price > 0, "Цена price должна быть больше нуля"


@dataclass(unsafe_hash=True)
class BookingDate(Model):
    date: date
    status: int  # ARRIVAL/DEPARTURE


@dataclass(unsafe_hash=True)
class Order(Model):
    # даты желаемого заезда и выезда
    dates: List[BookingDate]
    room: Optional[Room] = None
    booking: bool = False  # признак бронирования


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

    def get_access_token(self, email: str) -> str:
        return self._get_token(email, expires_delta=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    def get_refresh_token(self, email: str) -> str:
        return self._get_token(
            email,
            expires_delta=self.REFRESH_TOKEN_EXPIRE_MINUTES,
            audience=self.AUDIENCE,
        )

    @classmethod
    def init(cls, users: List[User]) -> "UserManager":
        res = {}
        for user in [i[0] for i in users]:
            res[user.email] = user
        return cls(res)
