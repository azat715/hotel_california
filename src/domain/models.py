import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import date, timedelta
from email.policy import default
from typing import Optional
from uuid import UUID, uuid4


class Model(ABC):
    pass
    # def __hash__(self) -> int:
    #     return hash(self.uuid)

    # def __eq__(self, other: "Model") -> bool:
    #     return self.uuid == other.uuid


@dataclass(unsafe_hash=True)
class Room(Model):
    number: int
    capacity: int
    price: float
    # uuid: UUID = field(default_factory=lambda: uuid4())
    # uuid: UUID = uuid4()

    def __post_init__(self):
        assert self.capacity > 0, "Bместительность capacity должно быть больше нуля"
        assert self.price > 0, "Цена price должна быть больше нуля"


@dataclass
class Order(Model):
    num_residents: int
    arrival_date: date
    departure_date: date
    booking: Optional[bool] = False
    room_num: Optional[int] = None
    # uuid: UUID = field(default_factory=lambda: uuid4())

    def __post_init__(self):
        assert self.num_residents > 0, "Количество проживающих должно быть больше нуля"
        assert (
            self.departure_date > self.arrival_date
        ), "Нельзя уехать раньше чем прибыть"
        if self.booking:
            assert self.room_num, "После бронирования должен быть номер комнаты"


@dataclass
class User(Model):
    name: str
    email: str  # должно быть уникальным
    is_admin: bool
    # uuid: UUID = field(default_factory=lambda: uuid4())
