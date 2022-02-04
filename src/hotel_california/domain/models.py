from abc import ABC
from datetime import date
from typing import List, Optional

from pydantic import EmailStr
from pydantic.dataclasses import dataclass


class NonUniqEmail(Exception):
    def __init__(self, email: str):
        message = f"Email {email} должен быть уникальным"
        super().__init__(message)


class Model(ABC):
    pass


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
class User(Model):
    name: str
    email: EmailStr  # должно быть уникальным
    is_admin: bool = False

    @property
    def check_admin(self) -> bool:
        return self.is_admin
