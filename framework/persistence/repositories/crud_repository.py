from typing import (
    Callable,
    Generic,
    Iterable,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    Union,
    get_args,
)
from uuid import UUID

from loguru import logger
from sqlalchemy import Select
from sqlmodel import Session, SQLModel, select
from sqlmodel.sql.expression import Select, SelectOfScalar

from framework.persistence.core.py_spring_model import PySpringModel, Transactional
from framework.persistence.repositories.repository_base import RepositoryBase

T = TypeVar("T", bound=SQLModel)
ID = TypeVar("ID", UUID, int)


class SQLConnectionParam(TypedDict):
    url: str

class CrudRepository(RepositoryBase, Generic[ID, T]):
    def __init__(self) -> None:
        self.engine = PySpringModel.get_engine()
        self.id_type, self.model_class = self._get_model_id_type_with_class()
        
        
    @classmethod
    def _get_model_id_type_with_class(cls) -> tuple[Type[ID], Type[T]]:
        return get_args(tp=cls.__mro__[0].__orig_bases__[0])

    def _conduct_operation_in_session(
        self,
        session_operation: Callable[[Session], None],
        session: Session,
    ) -> bool:
        try:
            session_operation(session)
        except Exception as error:
            logger.error(error)
            raise error

        return True
    
    @Transactional
    def _find_by(
        self,
        statement: Union[Select, SelectOfScalar],
        session: Optional[Session] = None,
    ) -> Optional[T]:
        if session is None:
            session = self._create_session()

        return session.exec(statement).first()

    @Transactional
    def _find_all_by(
        self,
        statement: Union[Select, SelectOfScalar],
        session: Optional[Session] = None,
    ) -> list[T]:
        if session is None:
            session = self._create_session()

        return list(session.exec(statement))

    def _create_session(self) -> Session:
        return Session(self.engine, expire_on_commit=False)
    
    @Transactional
    def find_by_id(self, id: ID, session: Optional[Session] = None) -> Optional[T]:
        if session is None:
            session = self._create_session()

        statement = select(self.model_class).where(self.model_class.id == id)  # type: ignore
        return session.exec(statement).first()

    @Transactional
    def find_all_by_ids(
        self, ids: list[ID], session: Optional[Session] = None
    ) -> list[T]:
        if session is None:
            session = self._create_session()
        statement = select(self.model_class).where(self.model_class.id.in_(ids))  # type: ignore
        return list(session.exec(statement).all())

    
    @Transactional
    def find_all(self, session: Optional[Session] = None) -> list[T]:
        if session is None:
            session = self._create_session()
        statement = select(self.model_class)  # type: ignore
        return list(session.exec(statement).all())
    
    @Transactional
    def save(
        self, entity: T, session: Optional[Session] = None
    ) -> T:
        self._conduct_operation_in_session(
            lambda session: session.add(entity),
            session or self._create_session()
        )
        return entity

    @Transactional
    def save_all(
        self,
        entities: Iterable[T],
        session: Optional[Session] = None,
    ) -> bool:
        return self._conduct_operation_in_session(
            lambda session: session.add_all(entities),
            session or self._create_session()
        )
        
    @Transactional
    def delete(
        self, entity: T, session: Optional[Session] = None
    ) -> bool:
        return self._conduct_operation_in_session(
            lambda session: session.delete(entity),
            session or self._create_session()
        )
        
    @Transactional
    def delete_all(
        self,
        entities: Iterable[T],
        session: Optional[Session] = None
    ) -> bool:
        session = session or self._create_session()
        for entity in entities:
            session.delete(entity)
        return True
    
    @Transactional
    def delete_by_id(
        self, id: ID, session: Optional[Session] = None
    ) -> bool:


        entity = self.find_by_id(id, session)
        if entity is not None:
            return self.delete(entity, session)
        return False
    
    @Transactional
    def delete_all_by_ids(
        self, ids: list[ID], session: Optional[Session] = None
    ) -> bool:
        entities = self.find_all_by_ids(ids, session)
        return self.delete_all(entities, session)