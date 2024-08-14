
from typing import Callable

from loguru import logger
from pydantic import BaseModel, Field, computed_field

from framework.core.entities.component import Component

class BeanView(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    bean_creation_func: Callable[..., Component] = Field(exclude= True)
    bean: object

    @computed_field
    @property
    def bean_name(self) -> str:
        return self.bean_creation_func.__annotations__['return'].__name__
    
    def is_valid_bean(self) -> bool:
        return self.bean_name == self.bean.__class__.__name__

class BeanConflictError(Exception): ...

class InvalidBeanError(Exception): ...

class BeanCollection:
    OBJECT_CREATION_IDENTIFIER = "create"
    """
    The `BeanCollection` class is a core entity in the framework. 
    It represents a basic building block that can be configured and wired together to create more complex applications.
    Sometimes automatic configuration is not an option, such as when working with 3rd-party libraries where the source code is not available as Component. 
    In these cases, the `BeanCollection` class provides a way to manually configure and wire the components.
    """

    @classmethod
    def scan_beans(cls) -> list[BeanView]:
        """
        Scans the beans within current class, use type annonation to get the component class.
        """
        bean_views: list[BeanView] = []
        for func_name in dir(cls):
            if not func_name.startswith(cls.OBJECT_CREATION_IDENTIFIER):
                continue
            
            func = getattr(cls, func_name)
            view = BeanView(bean_creation_func=func,bean= func())
            logger.success(f"[BEAN CREATION UNDER {cls.__name__}] Found bean creation func: {view.bean_creation_func.__name__} with bean name: {view.bean_name}")
            bean_views.append(view)

        return bean_views
    
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

            

            