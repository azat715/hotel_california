from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry

from hotel_california.domain.models import User

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


def start_mappers():
    mapper_registry.map_imperatively(User, user)


def create_all_tables(engine):
    metadata_obj.create_all(engine)
