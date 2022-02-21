from datetime import datetime, date

from pydantic import BaseModel, EmailStr, PositiveInt, PositiveFloat


class RoomFindSchema(BaseModel):
    """форма для поиска комнаты"""

    capacity: int
    arrival: datetime
    departure: datetime


class TokenResponse(BaseModel):
    access: str
    refresh: str


class UserLoginSchema(BaseModel):
    """логин пользователя"""

    email: EmailStr
    password: str


class UserForm(BaseModel):
    name: str
    email: str  # должно быть уникальным
    password: str  # пароль
    is_admin: bool = False


class RoomAddForm(BaseModel):
    number: PositiveInt
    capacity: PositiveInt
    price: PositiveFloat


class RoomResponse(BaseModel):
    number: PositiveInt
    capacity: PositiveInt
    price: PositiveFloat


class OrderResponse(BaseModel):
    identity: int
    arrival: date
    departure: date

