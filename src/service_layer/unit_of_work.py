from abc import ABC, abstractmethod

from adapters.repository import AbstractRepository, FakeDb


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
