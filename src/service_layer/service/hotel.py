from datetime import date
from typing import List, Optional

from domain.models import Order, Room
from service_layer.exceptions import RoomExistError
from service_layer.unit_of_work import AbstractUnitOfWork

# должен ли я объединить эти функции в класс который содержит в себе workers?


def add_room(number: int, capacity: int, price: float, workers: AbstractUnitOfWork):
    """добавление комнаты"""
    with workers as worker:
        room = Room(number=number, capacity=capacity, price=price)
        if worker.data.exists(room):
            raise RoomExistError(number)
        worker.data.add(room)
        worker.commit()


def get_room_by_cap(cap: int, workers: AbstractUnitOfWork) -> List[Room]:
    """список комнат с вместимостью cap"""
    with workers as worker:
        return worker.data.filter({"capacity": cap})


def get_orders_by_room_nums(
    room_nums: List[int], workers: AbstractUnitOfWork
) -> List[Order]:
    with workers as worker:
        return worker.data.filter({"room_num": room_nums, "booking": True})


def find_room(
    num_residents: int,
    arrival_date: date,
    departure_date: date,
    workers: AbstractUnitOfWork,
) -> Optional[List[Room]]:
    rooms = get_room_by_cap(num_residents, workers)
    orders = get_orders_by_room_nums([i.number for i in rooms], workers)
    d
