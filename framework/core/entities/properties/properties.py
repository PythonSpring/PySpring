from typing import ClassVar

from pydantic import BaseModel


class Properties(BaseModel):
    """
    Defines a base class `Properties` that provides a standard way to manage properties for entities in the application.

    The `Properties` class provides the following functionality:

    - Defines a class-level `__key__` attribute that can be set to a unique string identifier for the properties class.
    - Provides a `get_key()` class method that returns the value of the `__key__` attribute, raising a `ValueError` if it is not set.
    - Provides a `get_name()` class method that returns the name of the class.

    Subclasses of `Properties` should define the `__key__` attribute to provide a unique identifier for the properties they represent.
    """

    __key__: ClassVar[str] = ""

    @classmethod
    def get_key(cls) -> str:
        _key = cls.__key__
        if _key is None or _key == "":
            raise ValueError(
                f"[KEY NOT SET] Properties key is not set for class: {cls.__name__}"
            )
        return cls.__key__

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
