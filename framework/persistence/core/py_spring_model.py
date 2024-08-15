from typing import ClassVar, Optional

from sqlalchemy import Engine
from sqlmodel import SQLModel


class PySpringModel(SQLModel):
    """
    Represents a PySpring model, which is a subclass of SQLModel.
    
    The `engine` class variable is an optional reference to an SQLAlchemy Engine instance,
    which can be used for database operations related to this model.
    """
        
    engine: ClassVar[Optional[Engine]] = None
