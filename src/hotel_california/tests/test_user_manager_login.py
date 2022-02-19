import pytest

from hotel_california.domain.models import UserManager
from hotel_california.service_layer.exceptions import InvalidPassword


@pytest.fixture
def manager():
    manager = UserManager(users={})
    user = manager.create(
        name="test_user",
        email="test@email.com",
        password='test_hash',
        is_admin=True
    )
    return UserManager(users={
        user.email: user
    })


def test_login(manager):
    user = manager.login(email="test@email.com", password="test_hash")
    assert user.email == "test@email.com"


def test_fail_login(manager):
    with pytest.raises(InvalidPassword):
        manager.login(email="test@email.com", password="not_valid_pass")
