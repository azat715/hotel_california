from fastapi import APIRouter, Request, Response, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.authentication import requires

from hotel_california.config import get_settings
from hotel_california.entrypoints.app.forms import LoginForm, RoomForm, DatesForm, UserForm
from hotel_california.entrypoints.app.workers import get_user_worker, get_room_worker, get_order_worker
from hotel_california.service_layer.service.hotel import get_access_token, get_rooms, add_room, get_room_orders, \
    booking, delete_order, add_user, get_users
from hotel_california.service_layer.unit_of_work import UOW

settings = get_settings()

TEMPLATE_DIR = str(settings.PATHS.fastapi_folder.joinpath(settings.PATHS.template_dir))
templates = Jinja2Templates(directory=TEMPLATE_DIR)

admin_router = APIRouter()


@admin_router.get("/admin/login")
@admin_router.post("/admin/login")
async def login(request: Request, worker: UOW = Depends(get_user_worker)):
    """

    Args:
        request:
        worker: User worker

    Returns:
        TemplateResponse форма логина

    """
    form = LoginForm(await request.form())

    if request.method == 'POST' and form.validate():
        response = RedirectResponse(url="/admin/rooms", status_code=status.HTTP_303_SEE_OTHER)
        token = get_access_token(form.email.data, form.password.data, workers=worker)
        print("Успех")
        print(form.email.data)
        print(form.password.data)
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {token}",
            domain='127.0.0.1',
            httponly=True,
            max_age=1800,
            expires=1800,
        )
        return response
    print(form.errors)
    return templates.TemplateResponse("login.html", {"request": request, 'form': form})


@admin_router.get("/admin/logout", response_class=RedirectResponse)
@requires(['authenticated'])
async def logout(request: Request, response: Response):
    """Разлогин и редирект
    """
    response.delete_cookie("Authorization")
    return "/admin/login"


@admin_router.get("/admin/rooms")
@requires(['authenticated'])
async def rooms_endpoint(request: Request, worker: UOW = Depends(get_room_worker)):
    """Список комнат
    """
    rooms = get_rooms(workers=worker)
    rooms = sorted(rooms, key=lambda x: x.number)
    return templates.TemplateResponse("rooms.html", {"request": request, 'rooms': rooms})


@admin_router.get("/admin/rooms/add")
@admin_router.post("/admin/rooms/add")
@requires(['authenticated', 'admin'])
async def room_add_endpoint(request: Request, worker: UOW = Depends(get_room_worker)):
    """Добавление комнаты

    только админ
    """
    form = RoomForm(await request.form())
    if request.method == 'POST' and form.validate():
        add_room(form.number.data, form.capacity.data, form.price.data, workers=worker)
        return RedirectResponse(url="/admin/rooms", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add_room.html", {"request": request, 'form': form})


@admin_router.get("/admin/rooms/{num}/orders")
@requires(['authenticated'])
async def room_get_orders_endpoint(request: Request, num: int, worker: UOW = Depends(get_room_worker)):
    """Список ордеров комнаты
    """
    orders = get_room_orders(num, worker)
    return templates.TemplateResponse("orders.html", {"request": request, 'orders': orders})


@admin_router.get("/admin/rooms/{num}/orders/add")
@admin_router.post("/admin/rooms/{num}/orders/add")
@requires(['authenticated'])
async def room_add_order_endpoint(request: Request, num: int, room_worker: UOW = Depends(get_room_worker), order_worker: UOW = Depends(get_order_worker)):
    """Забронировать номер

    (указываем номер, дата заезда, дата отъезда, возвращаем номер брони)"""
    form = DatesForm(await request.form())
    if request.method == 'POST' and form.validate():
        booking(num, form.arrival.data, form.departure.data, room_worker, order_worker)
        return RedirectResponse(url="/admin/rooms", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add_order.html", {"request": request, 'form': form})


@admin_router.get("/admin/orders/{order_id}/cancel")
@requires(['authenticated'])
async def booking_cancel_endpoint(request: Request, order_id: int, order_worker: UOW = Depends(get_order_worker)):
    """Отмена брони

    Args:
        request:
        order_id: номер Id брони
        order_worker:

    Returns:

    """
    delete_order(order_id, order_worker)
    return RedirectResponse(url="/admin/rooms", status_code=status.HTTP_303_SEE_OTHER)


@admin_router.get("/admin/users")
@requires(['authenticated', 'admin'])
async def users_endpoint(request: Request, worker: UOW = Depends(get_user_worker)):
    """Список пользователей
    """
    users = get_users(workers=worker)
    return templates.TemplateResponse("users.html", {"request": request, 'users': users})


@admin_router.get("/admin/users/add")
@admin_router.post("/admin/users/add")
@requires(['authenticated', 'admin'])
async def user_add_endpoint(request: Request, worker: UOW = Depends(get_user_worker)):
    """Добавление пользователя"""
    form = UserForm(await request.form())
    if request.method == 'POST' and form.validate():
        add_user(form.name.data, form.email.data, form.password.data, form.is_admin.data, workers=worker)
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add_user.html", {"request": request, 'form': form})
