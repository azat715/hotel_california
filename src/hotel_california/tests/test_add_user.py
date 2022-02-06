import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hotel_california.adapters.orm import create_all_tables, start_mappers
from hotel_california.adapters.repository import UserRepository
from hotel_california.domain.models import RefreshToken, User
from hotel_california.service_layer.exceptions import NonUniqEmail
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW


def test_add_user():
    """тест на создание users, вообще работу алхимии"""

    test_user = {"name": "test_user", "email": "test@email.com", "password": "12345678"}
    # вот эти части надо вынести в conftest
    ENGINE = create_engine("sqlite://")
    DEFAULT_SESSION_FACTORY = sessionmaker(bind=ENGINE)
    start_mappers()
    create_all_tables(ENGINE)

    worker = SqlAlchemyUOW(repo=UserRepository, session_factory=DEFAULT_SESSION_FACTORY)
    u = User(**test_user)
    t = RefreshToken(value="test")
    u.token = t
    add_user(u, workers=worker)

    with ENGINE.connect() as con:
        rs = con.execute("SELECT * FROM user")
        for row in rs:
            assert tuple(row) == (1, "test_user", "test@email.com", 0)
        rs = con.execute("SELECT * FROM token")
        for row in rs:
            assert tuple(row) == (1, 1, "test")

    u2 = User(**test_user)
    with pytest.raises(NonUniqEmail):
        add_user(u2, workers=worker)

    test_user_bad_pass = {
        "name": "test_user2",
        "email": "test2@email.com",
        "password": "1",
    }
    with pytest.raises(ValidationError):
        User(**test_user_bad_pass)
