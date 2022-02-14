from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from hotel_california.domain.models import AUDIENCE, LOGIN_URL
from hotel_california.entrypoints.app.workers import get_user_worker
from hotel_california.service_layer.service.hotel import check_is_admin, decode_token
from hotel_california.service_layer.unit_of_work import UOW

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_URL)


async def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    """валидация токена"""
    payload = decode_token(token)
    return payload


async def validate_refresh_token(token: str = Depends(oauth2_scheme)) -> dict:
    """валидация refresh токена"""
    payload = decode_token(token, audience=AUDIENCE)
    return payload


async def check_admin(
    payload: str = Depends(validate_token),
    worker: UOW = Depends(get_user_worker),
) -> dict:
    """проверка пользователя на админ"""
    email: str = payload.get("sub")
    check_is_admin(email=email, workers=worker)
