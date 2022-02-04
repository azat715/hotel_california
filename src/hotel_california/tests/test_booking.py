from datetime import date

import pytest
from hotel_california.domain.models import BookingDate
from hotel_california.service_layer.exceptions import RoomNonFree
from hotel_california.service_layer.service.hotel import Status, check_free_room


def test_find_room():
    pass


@pytest.fixture
def dates():
    return [
        BookingDate(date=date(2000, 1, 1), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 7), status=int(Status.DEPARTURE)),
        BookingDate(date=date(2000, 1, 14), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 23), status=int(Status.DEPARTURE)),
    ]


def test_check_free_room(dates):
    test_dates = (
        BookingDate(date=date(2000, 1, 8), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    check_free_room(test_dates, dates)


def test_check_free_room1(dates):
    # случай с выездом и заездом в один день
    test_dates = (
        BookingDate(date=date(2000, 1, 7), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    check_free_room(test_dates, dates)


def test_check_free_room2(dates):

    # случай с выездом и заездом в один день(и выезд в день заезда следующего клиента)
    test_dates = (
        BookingDate(date=date(2000, 1, 7), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    check_free_room(test_dates, dates)


def test_check_free_room_raise(dates):
    # пересечение заезда
    test_dates = (
        BookingDate(date=date(2000, 1, 6), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 10), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        check_free_room(test_dates, dates)


def test_check_free_room_raise1(dates):
    # пересечение выезда
    test_dates = (
        BookingDate(date=date(2000, 1, 8), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 15), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        check_free_room(test_dates, dates)


def test_check_free_room_raise2(dates):
    # пересечение заезда и выезда
    test_dates = (
        BookingDate(date=date(2000, 1, 2), status=int(Status.ARRIVAL)),
        BookingDate(date=date(2000, 1, 5), status=int(Status.DEPARTURE)),
    )
    with pytest.raises(RoomNonFree):
        check_free_room(test_dates, dates)
