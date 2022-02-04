import pytest
from hotel_california.adapters.orm import create_all_tables, start_mappers
from hotel_california.adapters.repository import UserRepository
from hotel_california.domain.models import NonUniqEmail, User
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.service_layer.unit_of_work import (
    DEFAULT_SESSION_FACTORY,
    ENGINE,
    SqlAlchemyUOW,
)


def test_add_user():
    """тест на создание users, вообще работу алхимии"""
    test_user = {
        "name": "test_user",
        "email": "test@email.com",
    }
    # вот эти части надо вынести в conftest
    start_mappers()
    create_all_tables(ENGINE)
    worker = SqlAlchemyUOW(repo=UserRepository, session_factory=DEFAULT_SESSION_FACTORY)
    u = User(**test_user)
    add_user(u, workers=worker)

    with ENGINE.connect() as con:
        #
        rs = con.execute("SELECT * FROM user")
        for row in rs:
            # pdb.set_trace()
            assert tuple(row) == (1, "test_user", "test@email.com", 0)

    u2 = User(**test_user)
    with pytest.raises(NonUniqEmail):
        add_user(u2, workers=worker)
