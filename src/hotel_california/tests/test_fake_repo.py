from adapters.repository import FakeDb
from domain.models import Room


def test_fake_repository_get_room():
    rooms = [Room(1, 1, 1), Room(2, 1, 1)]
    db = FakeDb(rooms)
    assert rooms[0] == db.get(
        {
            "number": 1,
        }
    )
    assert rooms[0] == db.get(
        {
            "number": 1,
            "capacity": 1,
        }
    )

    assert rooms[1] == db.get(
        {
            "number": 2,
            "capacity": 1,
        }
    )


def test_fake_repository_filter_room():
    rooms = [Room(1, 1, 5), Room(2, 1, 10), Room(3, 2, 15), Room(4, 2, 15)]
    db = FakeDb(rooms)
    diff = set(rooms[2:]) ^ set(db.filter({"capacity": 2, "price": 15}))
    assert not diff

    diff = set(rooms[:2]) ^ set(db.filter({"capacity": 1}))
    assert not diff
