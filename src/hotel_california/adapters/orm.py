from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table, SmallInteger, Float, Date, \
    Enum

from sqlalchemy.orm import registry, relationship

from hotel_california.domain.models import RefreshToken, User, Room, Status, Order, BookingDate

mapper_registry = registry()

metadata_obj = MetaData()

user = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    # тут я не могу поставить unique=True чтобы проверить уникальность емайлов
    Column("email", String),
    Column("password", String),
    Column("is_admin", Boolean),

)

refresh_token = Table(
    "refresh_token",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("value", String),
)

rooms = Table(
    "rooms",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("number", SmallInteger),
    Column("capacity", SmallInteger),
    Column("price", Float)
)

order = Table(
    "orders",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("room_id", Integer, ForeignKey("rooms.id")),
    Column("guest", String)
)

dates = Table(
    "dates",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("orders.id")),
    Column("date", Date),
    Column("status", Enum(Status))
)


def start_mappers():
    mapper_registry.map_imperatively(
        User,
        user,
        properties={"token": relationship(RefreshToken, backref="user", uselist=False)},
    )
    mapper_registry.map_imperatively(RefreshToken, refresh_token)

    mapper_registry.map_imperatively(
        Room,
        rooms,
        properties={"orders": relationship(Order, backref="room")})
    mapper_registry.map_imperatively(
        Order,
        order,
        properties={"dates": relationship(BookingDate, backref="order")})
    mapper_registry.map_imperatively(BookingDate, dates)


def create_all_tables(engine):
    metadata_obj.create_all(engine)
