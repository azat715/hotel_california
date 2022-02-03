import pdb

import pytest
from adapters.orm import create_all_tables, start_mappers
from service_layer.service.hotel import add_user
from service_layer.unit_of_work import DEFAULT_SESSION_FACTORY, ENGINE, SqlAlchemyUOW
from sqlalchemy.exc import IntegrityError


def test_add_user():
    """тест на создание users, вообще работу алхимии"""
    test_user = {
        "name": "test_user",
        "email": "test@email.com",
    }
    start_mappers()
    create_all_tables(ENGINE)
    worker = SqlAlchemyUOW(DEFAULT_SESSION_FACTORY)
    add_user(**test_user, workers=worker)

    with ENGINE.connect() as con:
        #
        rs = con.execute("SELECT * FROM user")
        for row in rs:
            # pdb.set_trace()
            assert tuple(row) == (1, "test_user", "test@email.com", 0)

    with pytest.raises(IntegrityError):
        add_user(**test_user, workers=worker)
