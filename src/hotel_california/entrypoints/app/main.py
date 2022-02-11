from datetime import date

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from hotel_california.adapters.orm import start_mappers
from hotel_california.config import get_settings
from hotel_california.domain.models import User, Room, Order, BookingDate, Status
from hotel_california.entrypoints.app.auth_bearer import check_admin
from hotel_california.entrypoints.app.routers.auth import auth_router
from hotel_california.entrypoints.app.workers import user_worker, room_worker
from hotel_california.service_layer.exceptions import (
    AuthenticationError,
    BusinessLogicError,
)
from hotel_california.service_layer.service.hotel import add_user, add_room
from hotel_california.service_layer.unit_of_work import UOW

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
start_mappers()

app.include_router(auth_router)


@app.exception_handler(BusinessLogicError)
async def logic_exception_handler(request: Request, exc: BusinessLogicError):
    return JSONResponse(
        status_code=422,
        content={"message": "Error! BusinessLogicError", "body": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Error! ParseError", "body": exc.errors()},
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"message": "Error! AuthenticationError", "body": str(exc)},
    )


@app.get("/test")
async def test():
    return {"message": "Hello World"}


@app.post("/users", dependencies=[Depends(check_admin)])
async def add_user_endpoint(
    user: User,
    worker: UOW = Depends(user_worker),
):
    add_user(user, workers=worker)




class Item(BaseModel):
    number: int  # номер комнаты, уникальный
    capacity: int
    price: float


@app.post("/rooms")
async def add_room_endpoint(item: Item, worker: UOW = Depends(room_worker)):
    room = Room(2, 1, 100, orders=[Order(guest="test")])
    add_room(room, workers=worker)


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
