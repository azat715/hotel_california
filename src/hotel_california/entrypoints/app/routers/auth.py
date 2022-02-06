from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, EmailStr

from hotel_california.entrypoints.app.auth_bearer import (
    validate_refresh_token,
    validate_token,
)
from hotel_california.entrypoints.app.workers import user_worker
from hotel_california.service_layer.service.hotel import login_user

auth_router = APIRouter()


class TokenResponse(BaseModel):
    access: str
    refresh: str


class UserLoginSchema(BaseModel):
    """логин пользователя"""

    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "examples": [
                {
                    "email": "test@mail.com",
                    "password": "123",
                }
            ]
        }


@auth_router.post("users/login", response_model=TokenResponse)
async def user_login(data: UserLoginSchema = Body(...)):
    login_user(**data, workers=user_worker)


@auth_router.get("/test2", dependencies=[Depends(validate_token)])
async def root():
    """тестовый апи с аутентификацией"""
    return {"message": "Hello World"}
