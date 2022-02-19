from fastapi import Depends

from hotel_california.adapters.orm import start_mappers
from hotel_california.adapters.repository import UserRepository, RoomRepository, OrderRepository
from hotel_california.adapters.sqlalchemy_init import SessionLocal
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW

start_mappers()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_worker(session=Depends(get_db)):
    return SqlAlchemyUOW(repo=UserRepository, session=session)


def get_room_worker(session=Depends(get_db)):
    return SqlAlchemyUOW(repo=RoomRepository, session=session)


def get_order_worker(session=Depends(get_db)):
    return SqlAlchemyUOW(repo=OrderRepository, session=session)
