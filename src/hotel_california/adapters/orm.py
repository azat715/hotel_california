from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

from hotel_california.domain.models import RefreshToken, User

mapper_registry = registry()

metadata_obj = MetaData()

user = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String()),
    # тут я не могу поставить unique=True чтобы проверить уникальность емайлов
    Column("email", String()),
    Column("is_admin", Boolean),
)

refresh_token = Table(
    "refresh_token",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("value", String()),
)


def start_mappers():
    mapper_registry.map_imperatively(
        User,
        user,
        properties={"token": relationship(RefreshToken, backref="user", uselist=False)},
    )
    mapper_registry.map_imperatively(RefreshToken, refresh_token)


def create_all_tables(engine):
    metadata_obj.create_all(engine)
