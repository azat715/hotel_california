from fastapi import APIRouter, Depends

from hotel_california.entrypoints.app.auth_bearer import check_admin
from hotel_california.entrypoints.app.serializers import UserForm
from hotel_california.entrypoints.app.workers import get_user_worker
from hotel_california.service_layer.service.hotel import add_user
from hotel_california.service_layer.unit_of_work import UOW


users_router = APIRouter()


@users_router.post("/users", dependencies=[Depends(check_admin)])
async def add_user_endpoint(
    user: UserForm,
    worker: UOW = Depends(get_user_worker),
):
    add_user(**user.dict(), workers=worker)
