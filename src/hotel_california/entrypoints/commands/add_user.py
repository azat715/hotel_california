"""чтото типа django shell"""
from hotel_california.adapters.orm import start_mappers
from hotel_california.config import get_settings
from hotel_california.entrypoints.app.serializers import UserForm
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.adapters.repository import UserRepository
from hotel_california.adapters.sqlalchemy_init import SessionLocal
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW

settings = get_settings()

start_mappers()


def add_user_cmd():
    db = SessionLocal()
    worker = SqlAlchemyUOW(repo=UserRepository, session=db)
    user = UserForm(
        name="test_user",
        email="test_user@email.com",
        password="длинный_пассворд",
        is_admin=True,
    )
    try:
        add_user(**user.dict(), workers=worker)
    finally:
        db.close()


if __name__ == "__main__":
    add_user_cmd()
