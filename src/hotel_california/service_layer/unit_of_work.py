from abc import ABC, abstractmethod

from hotel_california.adapters.repository import (
    AbstractRepository,
    FakeDb,
    UserRepository,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


class AbstractUOW(ABC):
    data: AbstractRepository

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()
        if exc_val:
            raise exc_val


class FakeUnitOfWork(AbstractUOW):
    def __init__(self, db: AbstractRepository):
        self.data = db
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def __enter__(self):
        return self


ENGINE = create_engine("postgresql://test_db_user:123@db")
DEFAULT_SESSION_FACTORY = sessionmaker(bind=ENGINE)


class SqlAlchemyUOW(AbstractUOW):
    def __init__(
        self, repo: AbstractRepository, session_factory=DEFAULT_SESSION_FACTORY
    ):
        self.session_factory = session_factory
        self.session = self.session_factory()  # type: Session
        self.data = repo(self.session)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
