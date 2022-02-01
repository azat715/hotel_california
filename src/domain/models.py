from abc import ABC
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID, uuid4


class Model(ABC):
    pass
    # def __hash__(self) -> int:
    #     return hash(self.uuid)

    # def __eq__(self, other: "Model") -> bool:
    #     return self.uuid == other.uuid


@dataclass(unsafe_hash=True)
class Room(Model):
    """комната"""

    number: int  # номер комнаты, уникальный
    capacity: int
    price: float
    # uuid: UUID = field(default_factory=lambda: uuid4())
    # uuid: UUID = uuid4()

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

    # uuid: UUID = field(default_factory=lambda: uuid4())


@dataclass(unsafe_hash=True)
class User(Model):
    name: str
    email: str  # должно быть уникальным
    is_admin: bool
    # uuid: UUID = field(default_factory=lambda: uuid4())
