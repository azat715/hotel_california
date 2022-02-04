import pytest
from hotel_california.adapters.repository import FakeDb
from hotel_california.domain.models import Room
from hotel_california.service_layer.exceptions import RoomExistError
from hotel_california.service_layer.service.hotel import add_room, get_room_by_cap
from hotel_california.service_layer.unit_of_work import FakeUnitOfWork


def test_add_room():
    db = FakeDb([])
    fake_uow = FakeUnitOfWork(db)
    add_room(1, 1, 1, fake_uow)  # проверяю только то что нет exceptions
    # assert db._data == set([Room(1, 1)]) можно удалить это


def test_raise_duplicate_err():
    db = FakeDb([Room(1, 1, 1)])
    fake_uow = FakeUnitOfWork(db)
    with pytest.raises(RoomExistError):
        add_room(1, 1, 1, fake_uow)


def test_get_room_by_cap():
    rooms = [Room(1, 1, 1), Room(2, 1, 1), Room(3, 2, 1)]
    db = FakeDb(rooms)
    fake_uow = FakeUnitOfWork(db)
    res = get_room_by_cap(1, fake_uow)
    diff = set(rooms[:2]) ^ set(res)
    assert not diff
