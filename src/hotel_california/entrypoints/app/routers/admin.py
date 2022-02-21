from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.authentication import requires
from fastapi.responses import RedirectResponse

from hotel_california.config import get_settings
from hotel_california.entrypoints.app.forms import LoginForm, RoomForm
from hotel_california.service_layer.service.hotel import get_access_token, get_rooms, add_room
from hotel_california.entrypoints.app.workers import get_user_worker, get_room_worker
from hotel_california.service_layer.unit_of_work import UOW

settings = get_settings()

TEMPLATE_DIR = str(settings.PATHS.fastapi_folder.joinpath(settings.PATHS.template_dir))
templates = Jinja2Templates(directory=TEMPLATE_DIR)

admin_router = APIRouter()


@admin_router.get("/admin/check_admin", response_class=HTMLResponse)
@requires(['authenticated', 'admin'])
async def check_admin(request: Request):
    html_content = f"""
    <html>
        <body>
            <h1>is admin</h1>
            <h2>{request.user.is_admin}</h2>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@admin_router.get("/admin/check_not_admin", response_class=HTMLResponse)
@requires(['authenticated'])
async def check_not_admin(request: Request):
    html_content = f"""
    <html>
        <body>
            <h1>is not admin</h1>
            <h2>{request.user.is_admin}</h2>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@admin_router.get("/admin/login")
@admin_router.post("/admin/login")
async def login(request: Request, worker: UOW = Depends(get_user_worker)):
    form = LoginForm(await request.form())

    if request.method == 'POST' and form.validate():
        response = RedirectResponse("/admin/rooms")
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
    breakpoint()
    return templates.TemplateResponse("login.html", {"request": request, 'form': form})


@admin_router.get("/admin/logout", response_class=RedirectResponse)
@requires(['authenticated', 'admin'])
async def logout(request: Request, response: Response):
    response.delete_cookie("Authorization")
    return "/admin/login"


@admin_router.get("/admin/rooms")
@requires(['authenticated', 'admin'])
async def rooms_endpoint(request: Request, worker: UOW = Depends(get_room_worker)):
    rooms = get_rooms(workers=worker)
    rooms = sorted(rooms, key=lambda x: x.number)
    return templates.TemplateResponse("rooms.html", {"request": request, 'rooms': rooms})


@admin_router.get("/admin/rooms/add")
@admin_router.post("/admin/rooms/add")
@requires(['authenticated', 'admin'])
async def room_add_endpoint(request: Request, worker: UOW = Depends(get_room_worker)):
    form = RoomForm(await request.form())
    if request.method == 'POST' and form.validate():

        add_room(form.number.data, form.capacity.data, form.price.data, workers=worker)
        return RedirectResponse("/admin/rooms")
    return templates.TemplateResponse("add_room.html", {"request": request, 'form': form})
