"""чтото типа django shell"""
from hotel_california.adapters.orm import start_mappers
from hotel_california.config import get_settings
from hotel_california.entrypoints.app.serializers import UserForm
from hotel_california.entrypoints.app.workers import user_worker
from hotel_california.service_layer.service.hotel import add_user

settings = get_settings()

start_mappers()


def add_user_cmd():
    worker = user_worker()
    user = UserForm(
        name="test_user",
        email="test_user@email.com",
        password="длинный_пассворд",
        is_admin=True,
    )
    add_user(**user.dict(), workers=worker)


if __name__ == "__main__":
    add_user_cmd()
