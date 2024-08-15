from typing import ClassVar

from pydantic import BaseModel


class Properties(BaseModel):
    __key__: ClassVar[str] = ""

    @classmethod
    def get_key(cls) -> str:
        _key = cls.__key__
        if _key is None or _key == "":
            raise ValueError(f"[KEY NOT SET] Properties key is not set for class: {cls.__name__}")
        return cls.__key__

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
