

from typing import ClassVar, Optional
from sqlalchemy import Engine
from sqlmodel import SQLModel, Field


class PySpringModel(SQLModel):
    engine: ClassVar[Optional[Engine]] = None
    