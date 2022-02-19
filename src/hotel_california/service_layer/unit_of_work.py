from abc import ABC, abstractmethod

from sqlalchemy.orm.session import Session

from hotel_california.adapters.repository import AbstractRepository
from hotel_california.config import get_settings

settings = get_settings()


class UOW(ABC):
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


class FakeUnitOfWork(UOW):
    def __init__(self, db: AbstractRepository):
        self.data = db
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def __enter__(self):
        return self


class SqlAlchemyUOW(UOW):
    def __init__(
        self, repo: AbstractRepository, session: Session
    ):
        self.session = session
        self.data = repo(self.session)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
