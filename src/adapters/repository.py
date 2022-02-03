from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.models import Model
from sqlalchemy import select
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, model: Model):
        raise NotImplementedError

    @abstractmethod
    def get(
        self, reference: Dict[str, Any]
    ) -> Optional[Model]:  # возможно нужно Dict[str, Any]
        raise NotImplementedError

    @abstractmethod
    def filter(self, reference: Dict[str, Any]) -> List[Model]:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> List[Model]:
        raise NotImplementedError

    abstractmethod

    def exists(self, model: Model) -> bool:
        raise NotImplementedError


class FakeDb(AbstractRepository):
    def __init__(self, data: List[Model]) -> None:
        self._data = set(data)

    def _get(self, reference: Dict[str, Any], item: Model) -> Optional[Model]:
        res: Optional[Model] = item
        for field, value in reference.items():
            if not getattr(item, field) == value:
                res = None
        return res

    def _wrap_get(self, *args, **kwargs) -> bool:
        if self._get(*args, **kwargs):
            return True
        else:
            return False

    def get(self, reference: Dict[str, Any]) -> Optional[Model]:
        for item in self._data:
            if self._get(reference, item):
                return item

    def add(self, model: Model):
        self._data.add(model)

    def filter(self, reference: Dict[str, Any]) -> List[Model]:
        def check(reference):
            def wrapped(item):
                return self._wrap_get(reference, item)

            return wrapped

        t = check(reference)
        return list(filter(t, self._data))

    def all(self) -> List[Model]:
        return list(self._data)

    def exists(self, model: Model) -> bool:
        return model in self._data


class UserRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, model: Model):
        self.session.add(model)

    def get(self, model: Model, email: str) -> Optional[Model]:
        statement = select(model).filter_by(email=email)
        return self.session.execute(statement).one()

    def filter(self, reference: Dict[str, Any]) -> List[Model]:
        raise NotImplementedError

    def all(self) -> List[Model]:
        raise NotImplementedError

    def exists(self, model: Model, email: str) -> bool:
        statement = select(model).where(email=email).exists()
        return self.session.execute(statement)
