from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from hotel_california.domain.models import AUDIENCE, LOGIN_URL
from hotel_california.service_layer.service.hotel import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_URL)


async def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    """валидация токена"""
    payload = decode_token(token)
    return payload


async def validate_refresh_token(token: str = Depends(oauth2_scheme)) -> dict:
    """валидация refresh токена"""
    payload = decode_token(token, audience=AUDIENCE)
    return payload
