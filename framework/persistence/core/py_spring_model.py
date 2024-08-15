from typing import ClassVar, Optional

from sqlalchemy import Engine
from sqlmodel import SQLModel


class PySpringModel(SQLModel):
    engine: ClassVar[Optional[Engine]] = None
