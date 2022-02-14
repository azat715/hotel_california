from fastapi import APIRouter, Body, Depends

from hotel_california.entrypoints.app.auth_bearer import validate_refresh_token
from hotel_california.entrypoints.app.serializers import TokenResponse, UserLoginSchema
from hotel_california.entrypoints.app.workers import get_user_worker
from hotel_california.service_layer.service.hotel import login_user, refresh_token
from hotel_california.service_layer.unit_of_work import UOW

auth_router = APIRouter()


@auth_router.post("/users/login", response_model=TokenResponse)
async def user_login_endpoint(
    data: UserLoginSchema = Body(...), worker: UOW = Depends(get_user_worker)
):
    access, refresh = login_user(**data.dict(), workers=worker)
    return TokenResponse(access=access, refresh=refresh)


@auth_router.get("/users/refresh_token", response_model=TokenResponse)
async def refresh_token_endpoint(
    payload: str = Depends(validate_refresh_token),
    worker: UOW = Depends(get_user_worker),
):
    email: str = payload.get("sub")
    access, refresh = refresh_token(email, workers=worker)
    return TokenResponse(access=access, refresh=refresh)
