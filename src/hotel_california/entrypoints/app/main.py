from fastapi import FastAPI

app = FastAPI()


@app.get("/test")
async def test():
    return {"message": "Hello World"}


@app.post("/users")
async def add_user():
    pass


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
