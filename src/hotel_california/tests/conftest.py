import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

from hotel_california.adapters.orm import metadata_obj
from hotel_california.entrypoints.app.main import app
from hotel_california.entrypoints.app.workers import get_db


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False})


@pytest.fixture(scope="session")
def tables(engine):
    metadata_obj.create_all(engine)
    yield
    metadata_obj.drop_all(engine)


@pytest.fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture()
def client(dbsession):
    def override_get_db():
        try:
            db = dbsession
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
