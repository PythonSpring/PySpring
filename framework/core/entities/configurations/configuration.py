from typing import ClassVar
from pydantic import BaseModel

class Configuration(BaseModel):
    __key__: ClassVar[str] = ""

    
    @classmethod
    def get_key(cls) -> str:
        return cls.__key__