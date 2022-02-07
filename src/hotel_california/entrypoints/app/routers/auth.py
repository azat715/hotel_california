from fastapi import APIRouter, Body, Depends

from hotel_california.domain.models import TokenResponse, UserLoginSchema
from hotel_california.entrypoints.app.auth_bearer import (
    validate_refresh_token,
    validate_token,
)
from hotel_california.entrypoints.app.workers import user_worker
from hotel_california.service_layer.service.hotel import login_user
from hotel_california.service_layer.unit_of_work import AbstractUOW

auth_router = APIRouter()


@auth_router.post("/users/login", response_model=TokenResponse)
async def user_login(
    data: UserLoginSchema = Body(...), worker: AbstractUOW = Depends(user_worker)
):
    return login_user(data, workers=worker)


@auth_router.get("/test2", dependencies=[Depends(validate_token)])
async def root():
    """тестовый апи с аутентификацией"""
    return {"message": "Hello World"}
