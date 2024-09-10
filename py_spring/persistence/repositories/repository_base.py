from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Session

from py_spring.core.entities.component import Component
from py_spring.persistence.core.py_spring_model import PySpringModel

T = TypeVar("T", bound=BaseModel)


class RepositoryBase(Component):
    def __init__(self) -> None:
        self.engine = PySpringModel.get_engine()
        self.connection = PySpringModel.get_connection()

    def _execute_sql_returning_model(self, sql: str, model_cls: Type[T]) -> list[T]:
        cursor = self.connection.execute(text(sql))
        dict_results = [row._asdict() for row in cursor.fetchall()]
        results = [model_cls.model_validate(dict(row)) for row in dict_results]
        cursor.close()
        return results

    def _create_session(self) -> Session:
        return PySpringModel.create_session()
