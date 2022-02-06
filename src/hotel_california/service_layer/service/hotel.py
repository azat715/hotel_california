import enum
from typing import List, Optional

from hotel_california.domain.models import (BookingDate, NonUniqEmail, Order,
                                            Room, User)
from hotel_california.service_layer.exceptions import (RoomExistError,
                                                       RoomNonFree)
from hotel_california.service_layer.unit_of_work import AbstractUOW


class Status(enum.IntEnum):
    ARRIVAL = 1
    DEPARTURE = 2


def add_user(user: User, workers: AbstractUOW):
    with workers as worker:
        if user.email in [i[0].email for i in worker.data.all()]:
            raise NonUniqEmail(user.email)
        worker.data.add(user)
        worker.commit()


def add_room(number: int, capacity: int, price: float, workers: AbstractUOW):
    """добавление комнаты"""
    with workers as worker:
        room = Room(number=number, capacity=capacity, price=price)
        if worker.data.exists(room):
            raise RoomExistError(number)
        worker.data.add(room)
        worker.commit()


def get_room_by_cap(cap: int, workers: AbstractUOW) -> List[Room]:
    """список комнат с вместимостью cap"""
    return workers.data.filter({"capacity": cap})


def get_room_by_num(room_number: int, workers: AbstractUOW) -> Optional[Room]:
    """комната по номеру"""
    return workers.data.get({"number": room_number})


def get_room_bookings_by_num(num: int, workers: AbstractUOW) -> List[BookingDate]:
    return [i.dates for i in workers.data.filter({"room_num": num})]


def check_free_room(test_dates: tuple[BookingDate], dates: List[BookingDate]):
    """проверка свободна ли комната

    Args:
        test_dates tuple): кортеж дат прибытия/убытия
        dates (List[BookingDate]): кортеж дат прибытия/убытия существующих заказов

    Raises:
        RoomNonFree: Если комната не свобода то RoomNonFree
    """

    # добавляю существующие брони
    dates.extend(test_dates)
    # сортирую по времени
    dates.sort(key=lambda x: x.date)
    # если идут два подряд заезда/выезда ошибка

    while dates:
        first = dates.pop(0)
        second = dates.pop(0)
        if second.status == first.status:
            raise RoomNonFree()


def check_free_rooms(rooms: List[Room], dates: tuple[BookingDate]) -> List[Room]:
    free_rooms = []
    for room in rooms:
        try:
            check_free_room(room, dates)
        except RoomNonFree:
            pass
        else:
            free_rooms.append(room)
    return free_rooms


def booking_room(room: Room, dates: tuple[BookingDate], workers: AbstractUOW):
    with workers as worker:
        order = Order(dates, room, booking=True)
        worker.data.add(order)
        worker.commit()
