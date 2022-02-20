from functools import lru_cache

from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FASTAPI_DIR = BASE_DIR.joinpath('entrypoints', 'app')


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


class DatabaseSqlalchemy(BaseSettings):
    """вот эту часть думаю можно менять чтобы добавить mysql"""

    dialect: str = "postgresql"
    credentials: Credentials = Credentials()

    @property
    def url(self):
        return f"{self.dialect}://{self.credentials.user}:{self.credentials.password}@{self.credentials.host}:{self.credentials.port}/{self.credentials.database}"


class Security(BaseSettings):
    SECRET_KEY: str = "insecure_mock"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class Folders(BaseSettings):
    base_folder: Path = BASE_DIR
    fastapi_folder = FASTAPI_DIR
    static_folder: str = "static"
    template_dir: str = "templates"


class Settings(BaseSettings):
    APP_NAME = "hotel_california"
    DB: DatabaseSqlalchemy = DatabaseSqlalchemy()
    AUTH: Security = Security()
    PATHS: Folders = Folders()

    class Config:
        case_sensitive: bool = True


@lru_cache()
def get_settings():
    return Settings()
