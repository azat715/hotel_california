from datetime import datetime

from pydantic import BaseModel, EmailStr


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
    password: str  # hash пароля
    is_admin: bool = False
