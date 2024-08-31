from typing import ClassVar, Iterable, Optional

from sqlalchemy import Engine, MetaData
from sqlalchemy.engine.base import Connection
from sqlmodel import Session, SQLModel





class PySpringModel(SQLModel):
    """
    Represents a PySpring model, which is a subclass of SQLModel.

    The `engine` class variable is an optional reference to an SQLAlchemy Engine instance,
    which can be used for database operations related to this model.
    """

    _engine: ClassVar[Optional[Engine]] = None
    _models: ClassVar[Optional[list[type["PySpringModel"]]]] = None
    _metadata: ClassVar[Optional[MetaData]] = None
    _connection: ClassVar[Optional[Connection]] = None

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
    def get_connection(cls) -> Connection:
        if cls._connection is not None:
            return cls._connection
        
        if cls._engine is None:
            raise ValueError("[ENGINE NOT SET] SQL Engine is not set")
        
        cls._connection = cls._engine.connect()
        return cls._connection

    @classmethod
    def get_metadata(cls) -> MetaData:
        if cls._metadata is None:
            raise ValueError("[METADATA NOT SET] SQL MetaData is not set")
        return cls._metadata

    @classmethod
    def get_model_lookup(cls) -> dict[str, type["PySpringModel"]]:
        if cls._models is None:
            raise ValueError("[MODEL_LOOKUP NOT SET] Model lookup is not set")
        return {str(_model.__tablename__): _model for _model in cls._models}

    @classmethod
    def create_session(cls) -> Session:
        engine = cls.get_engine()
        return Session(engine, expire_on_commit=False)
    
    
    @classmethod
    def create_managed_session(cls) -> Iterable[Session]:
        """
        Creates a managed session context that will automatically close the session when the context is exited.
        ## Example Syntax:
            with PySpringModel.create_managed_session() as session:
                Do something with the session
                The session will be automatically closed when the context is exited
        
        """
                
        with cls.create_session() as session:
            yield session



