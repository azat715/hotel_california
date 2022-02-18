from dataclasses import asdict
from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from hotel_california.domain.models import Room, Order
from hotel_california.entrypoints.app.auth_bearer import validate_token
from hotel_california.entrypoints.app.serializers import RoomAddForm, RoomResponse, OrderResponse
from hotel_california.entrypoints.app.workers import get_room_worker, get_order_worker
from hotel_california.service_layer.service.hotel import add_room, find_rooms, check_room, create_order, \
    get_order_by_id, get_room_by_num, delete_order, get_room_orders
from hotel_california.service_layer.unit_of_work import UOW

rooms_router = APIRouter()


def convert_order(order: Order) -> dict:
    res = {"identity": order.identity}
    for i in order.dates:
        res[i.status] = i.date
    return res


@rooms_router.post("/rooms", dependencies=[Depends(validate_token)])
async def add_room_endpoint(room: RoomAddForm, worker: UOW = Depends(get_room_worker)):
    number = add_room(**room.dict(), workers=worker)
    return JSONResponse(
        status_code=201,
        content={"room_num": number},
    )


@rooms_router.get("/rooms", dependencies=[Depends(validate_token)],
                  response_model=List[RoomResponse],
                  response_model_exclude={"orders"})
async def find_rooms_endpoint(cap: int, arrival: date, departure: date, worker: UOW = Depends(get_room_worker)):
    """Поиск номера

    (указываем даты и количество мест,
    возвращаем список (номер, вместительность, цена)"""
    res: List[Room] = find_rooms(cap, arrival, departure, workers=worker)
    return [asdict(i) for i in res]


@rooms_router.get("/rooms/{num}/booking", dependencies=[Depends(validate_token)])
async def booking_room_endpoint(num: int, arrival: date, departure: date,
                                room_worker: UOW = Depends(get_room_worker),
                                order_worker: UOW = Depends(get_order_worker)):
    """Забронировать номер

    (указываем номер, дата заезда, дата отъезда, возвращаем номер брони)"""
    room = check_room(num, arrival, departure, workers=room_worker)
    order = create_order(arrival, departure, workers=order_worker)
    identity = order.identity
    room.orders.append(order)
    with room_worker as worker:
        worker.data.add(room)
        worker.commit()
    return JSONResponse(
        status_code=200,
        content={"order_id": identity},
    )


@rooms_router.get("/rooms/{num}/orders", dependencies=[Depends(validate_token)], response_model=List[OrderResponse])
async def get_bookings_endpoint(num: int, room_worker: UOW = Depends(get_room_worker)):
    """Показать даты на которые забронирована комната

    (указываем номер комнаты, возвращаем список броней"""
    return get_room_orders(num, room_worker)


@rooms_router.get("/orders/{order_id}", dependencies=[Depends(validate_token)], response_model=OrderResponse,
                  response_model_exclude={"identity"})
async def get_order_endpoint(order_id: int, order_worker: UOW = Depends(get_order_worker)):
    """Получить информацию по брони

    (указываем номер брони, возвращаем дату заезда и дату отъезда)
    """
    res = get_order_by_id(order_id, order_worker)
    return res


@rooms_router.get("/orders/{order_id}/cancel", dependencies=[Depends(validate_token)])
async def booking_cancel_endpoint(order_id: int, order_worker: UOW = Depends(get_order_worker)):
    """Снять бронь с номера
55755
    (указываем номер брони,"""
    delete_order(order_id, order_worker)
    return JSONResponse(
        status_code=204
    )
