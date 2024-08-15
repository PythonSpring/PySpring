from typing import ClassVar, Optional

from sqlalchemy import Engine
from sqlmodel import Field, SQLModel


class PySpringModel(SQLModel):
    engine: ClassVar[Optional[Engine]] = None
