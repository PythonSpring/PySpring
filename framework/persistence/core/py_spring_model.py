from typing import ClassVar, Optional

from sqlalchemy import Engine
from sqlmodel import SQLModel


class PySpringModel(SQLModel):
    """
    Represents a PySpring model, which is a subclass of SQLModel.
    
    The `engine` class variable is an optional reference to an SQLAlchemy Engine instance,
    which can be used for database operations related to this model.
    """
        
    _engine: ClassVar[Optional[Engine]] = None


    @classmethod
    def set_engine(cls, engine: Engine) -> None:
        
        cls._engine = engine

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
