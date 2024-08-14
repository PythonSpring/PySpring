from typing import ClassVar
from pydantic import BaseModel

class Properties(BaseModel):
    __key__: ClassVar[str] = ""

    
    @classmethod
    def get_key(cls) -> str:
        return cls.__key__
    
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
    


