from datetime import date
import datetime
from typing import List, NamedTuple, Optional

class RoomRepo:
    """класс хранилище"""
    pass


class OrderRepo:
    pass


class Room(NamedTuple):
    number: int
    capacity: int


class Booking(NamedTuple):
    room_num: int


class Order(NamedTuple):
    uuid: str
    num_residents: int
    arrival_date: date
    departure_date: date
    booking: Optional[Booking] # если ордер выполняется то записывается бронь


class Hotel:
    def __init__(self, data: RoomRepo) -> None:
        self._data = data

    def add(self, room: Room):
        """добавление комнаты"""
        
        pass

    def get_by_cap(self, cap: int):
        """список комнат с вместимостью cap"""
        return [i for i in self._data if i.capacity == cap]


class HotelManager:
