from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Credentials(BaseSettings):
    host: str
    port: int = 5432
    database: str
    user: str
    password: str

    class Config:
        fields = {
            "host": {
                "env": "HOST",
            },
            "port": {
                "env": "PORT",
            },
            "database": {
                "env": "POSTGRES_DB",
            },
            "user": {
                "env": "POSTGRES_USER",
            },
            "password": {
                "env": "POSTGRES_PASSWORD",
            },
        }


class DatabaseAsyncpg(BaseSettings):
    """вот эту часть думаю можно менять чтобы добавить mysql"""

    engine: str
    credentials: Credentials = Credentials()

    class Config:
        fields = {
            "engine": {
                "env": "ENGINE",
            },
        }


class Security(BaseSettings):
    SECRET_KEY: str = "insecure_mock"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class Settings(BaseSettings):
    APP_NAME = "hotel_california"
    DB: DatabaseAsyncpg = DatabaseAsyncpg()
    AUTH: Security = Security()

    class Config:
        case_sensitive: bool = True


@lru_cache()
def get_settings():
    return Settings()
