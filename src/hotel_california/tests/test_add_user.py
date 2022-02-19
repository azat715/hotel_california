import pytest

from hotel_california.adapters.repository import UserRepository
from hotel_california.service_layer.exceptions import NonUniqEmail
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW


def test_add_user(dbsession, engine):
    """тест на создание users, вообще работу алхимии"""

    worker = SqlAlchemyUOW(repo=UserRepository, session=dbsession)
    name = "test_user"
    email = "test@email.com"
    password = "12345678"
    add_user(name, email,  password, is_admin=False, workers=worker)

    with engine.connect() as con:
        rs = con.execute("SELECT * FROM user")
        for row in rs:
            assert row[0] == 1
            assert row[1] == "test_user"
            assert row[2] == "test@email.com"
            assert row[3]
            assert row[4] == 0

    with pytest.raises(NonUniqEmail):
        add_user(name, email,  password, is_admin=False, workers=worker)

