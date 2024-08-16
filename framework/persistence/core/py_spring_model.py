import functools
from typing import Any, Callable, ClassVar, Optional, TypeVar

from loguru import logger
from sqlalchemy import Engine, MetaData
from sqlmodel import SQLModel, Session
class PySpringModel(SQLModel):
    """
    Represents a PySpring model, which is a subclass of SQLModel.
    
    The `engine` class variable is an optional reference to an SQLAlchemy Engine instance,
    which can be used for database operations related to this model.
    """
        
    _engine: ClassVar[Optional[Engine]] = None
    _models: ClassVar[Optional[list[type["PySpringModel"]]]] = None
    _metadata: ClassVar[Optional[MetaData]] = None

    @classmethod
    def set_metadata(cls, metadata: MetaData) -> None:
        cls._metadata = metadata


    @classmethod
    def set_engine(cls, engine: Engine) -> None:
        cls._engine = engine

    @classmethod
    def set_models(cls, models: list[type["PySpringModel"]]) -> None:
        cls._models = models

    @classmethod
    def get_engine(cls) -> Engine:
        """
        Returns the SQLAlchemy Engine instance associated with this model.

        Returns:
            The SQLAlchemy Engine instance.
        """
        if cls._engine is None:
            raise ValueError("[ENGINE NOT SET] SQL Engine is not set")
        
        return cls._engine
    
    @classmethod
    def get_metadata(cls) -> MetaData:
        if cls._metadata is None:
            raise ValueError("[METADATA NOT SET] SQL MetaData is not set")
        return cls._metadata
    
    @classmethod
    def get_model_lookup(cls) -> dict[str, type["PySpringModel"]]:
        if cls._models is None:
            raise ValueError("[MODEL_LOOKUP NOT SET] Model lookup is not set")
        return {str( _model.__tablename__): _model for _model in cls._models }
    
    @classmethod
    def create_session(cls) -> Session:
        engine = cls.get_engine()
        return Session(engine, expire_on_commit=False)
         

FT = TypeVar("FT", bound=Callable[..., Any])
def Transactional(func: FT) -> FT:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Start a new session
        session: Session = PySpringModel.create_session()
        try:
            # Inject the session into the function's arguments
            if not isinstance(kwargs.get("session"), Session):
                kwargs['session'] = session
            
            result = func(*args, **kwargs)
            # Commit the transaction if everything went well
            session.commit()
            return result
        except Exception as error:
            # Rollback the transaction in case of an exception
            session.rollback()
            logger.exception(error)
            raise error
        finally:
            # Close the session
            session.close()
    
    return wrapper # type: ignore