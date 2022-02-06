from fastapi import Depends, FastAPI

from hotel_california.adapters.orm import create_all_tables, start_mappers
from hotel_california.adapters.repository import UserRepository
from hotel_california.domain.models import User
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.service_layer.unit_of_work import (
    DEFAULT_SESSION_FACTORY, ENGINE, AbstractUOW, SqlAlchemyUOW)

app = FastAPI()
start_mappers()


def user_worker():
    create_all_tables(ENGINE)
    return SqlAlchemyUOW(repo=UserRepository, session_factory=DEFAULT_SESSION_FACTORY)


@app.get("/test")
async def test():
    return {"message": "Hello World"}


@app.post("/users")
async def add_user_endpoint(user: User, worker: AbstractUOW = Depends(user_worker)):
    add_user(user, workers=worker)


@app.post("/rooms")
async def add_room():
    pass


@app.get("/rooms")
async def find_room():
    """Поиск номера

    (указываем даты и количество мест,
    возвращаем список (номер, вместительность, цена)"""


@app.post("/booking")
async def booking_room():
    """Забронировать номер

    (указываем номер, дата заезда, дата отъезда, возвращаем номер брони)"""


@app.get("/booking")
async def get_booking():
    """Получить информацию по брони

    (указываем номер брони, возвращаем дату заезда и дату отъезда)
    """


@app.get("/booking")
async def booking_cancel():
    """Снять бронь с номера

    (указываем номер брони,"""


@app.get("/booking")
async def get_bookings():
    """Показать даты на которые забронирована комната

    (указываем номер комнаты, возвращаем список (номер брони, вместительность, цена)"""
