from abc import ABC

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser, BaseUser, UnauthenticatedUser
)

from hotel_california.adapters.repository import UserRepository
from hotel_california.adapters.sqlalchemy_init import SessionLocal
from hotel_california.service_layer.service.hotel import decode_token, get_user_by_email
from hotel_california.service_layer.unit_of_work import SqlAlchemyUOW


class User(BaseUser, ABC):
    def __init__(self, email: str, is_admin=False) -> None:
        self.email = email
        self.is_admin = is_admin

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class SessionAuthBackend(AuthenticationBackend):
    """
            response.set_cookie(
            "Authorization",
            value=f"Bearer {token}",
            domain="localtest.me",
            httponly=True,
            max_age=1800,
            expires=1800,
        )
    """
    async def authenticate(self, conn):
        if "Authorization" in conn.headers:
            # пропускаю чтобы работала JWT
            return
        cookie_authorization: str = conn.cookies.get("Authorization")
        if cookie_authorization:
            _, token = cookie_authorization.split(" ")
            credentials = decode_token(token)
            email = credentials['sub']
            session = SessionLocal()
            worker = SqlAlchemyUOW(repo=UserRepository, session=session)
            user = get_user_by_email(email, workers=worker)
            print(cookie_authorization)

            if user.is_admin:
                return AuthCredentials(["authenticated", "admin"]), User(email, is_admin=user.is_admin)
            else:
                return AuthCredentials(["authenticated"]), User(email, is_admin=user.is_admin)
        else:
            return
