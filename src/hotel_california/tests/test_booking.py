from datetime import date

import pytest

from hotel_california.domain.models import BookingDate, Room, Order
from hotel_california.service_layer.exceptions import RoomNonFree
from hotel_california.service_layer.service.hotel import Status, RoomManager


@pytest.fixture
def manager():
    return RoomManager(
        rooms={
            1: Room(
                number=1,
                capacity=1,
                price=100,
                orders=[
                    Order(
                        identity=1,
                        dates=[
                            BookingDate(date=date(2000, 1, 1), status=int(Status.ARRIVAL)),
                            BookingDate(date=date(2000, 1, 7), status=int(Status.DEPARTURE)),
                        ]
                    ),
                    Order(
                        identity=2,
                        dates=[
                            BookingDate(date=date(2000, 1, 14), status=int(Status.ARRIVAL)),
                            BookingDate(date=date(2000, 1, 23), status=int(Status.DEPARTURE)),
                        ]
                    )
                ]
            )}
    )


def test_check_free_room(manager):
    test_dates = (
        BookingDate(date=date(2000, 1, 8), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    manager.check_room(1, test_dates)


def test_check_free_room1(manager):
    # случай с выездом и заездом в один день
    test_dates = (
        BookingDate(date=date(2000, 1, 7), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    manager.check_room(1, test_dates)


def test_check_free_room2(manager):
    # случай с выездом и заездом в один день(и выезд в день заезда следующего клиента)
    test_dates = (
        BookingDate(date=date(2000, 1, 7), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    manager.check_room(1, test_dates)


def test_check_free_room_raise(manager):
    # пересечение заезда
    test_dates = (
        BookingDate(date=date(2000, 1, 6), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        manager.check_room(1, test_dates)


def test_check_free_room_raise1(manager):
    # пересечение выезда
    test_dates = (
        BookingDate(date=date(2000, 1, 8), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 15), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        manager.check_room(1, test_dates)


def test_check_free_room_raise2(manager):
    # пересечение заезда и выезда
    test_dates = (
        BookingDate(date=date(2000, 1, 2), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 5), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        manager.check_room(1, test_dates)
