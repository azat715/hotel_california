from unittest.mock import MagicMock

import pytest

from hotel_california.domain.models import UserManager, User
from hotel_california.service_layer.exceptions import UserNotAdmin, NotFoundEmail
from hotel_california.service_layer.service.hotel import decode_token

USER1 = User(
    name="test_user",
    email="test@email.com",
    password='test_hash',
    is_admin=True
)

USER2 = User(
    name="test2_user",
    email="test2@email.com",
    password='test2_hash',
    is_admin=False
)


def test_create_user():
    manager = UserManager(users={})
    manager._hash_password = MagicMock(return_value='test_hash')
    user = USER1
    test_user = manager.create(
        name="test_user",
        email="test@email.com",
        password='test_hash',
        is_admin=True
    )
    assert test_user == user


@pytest.fixture
def manager():
    return UserManager(users={
        USER1.email: USER1,
        USER2.email: USER2
    }
    )


def test_check_admin(manager):
    assert manager.check_admin(email="test@email.com")
    with pytest.raises(UserNotAdmin):
        manager.check_admin(email="test2@email.com")


def test_get_user_by_email(manager):
    u = manager.get_user_by_email(email="test@email.com")
    assert u == USER1
    with pytest.raises(NotFoundEmail):
        manager.get_user_by_email(email="not_user@email.com")


def test_get_refresh_token(manager):
    token = manager.get_refresh_token(email="test@email.com")
    res = decode_token(token, audience="/users/token/refresh/")
    assert res["aud"] == '/users/token/refresh/'
    assert res['exp']
    assert res['iss'] == 'hotel_california'
    assert res['sub'] == 'test@email.com'


def test_get_access_token(manager):
    token = manager.get_access_token(email="test@email.com")
    res = decode_token(token)
    assert res['exp']
    assert res['iss'] == 'hotel_california'
    assert res['sub'] == 'test@email.com'
