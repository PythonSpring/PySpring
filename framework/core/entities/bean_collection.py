
from typing import Callable

from loguru import logger
from pydantic import BaseModel, Field

from framework.core.entities.component import Component
from framework.core.entities.properties.properties_loader import _PropertiesLoader
class BeanView(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    bean_creation_func: Callable[..., Component] = Field(exclude= True)
    bean_name: str
    bean: object

    def is_valid_bean(self) -> bool:
        return self.bean_name == self.bean.__class__.__name__

class BeanConflictError(Exception): ...

class InvalidBeanError(Exception): ...

class BeanCollection:
    OBJECT_CREATION_IDENTIFIER = "create"
    RETURN_KEY = "return"

    @classmethod
    def scan_beans(cls) -> list[BeanView]:
        """
        Scans the beans within current class, use type annotation to get the component class.
        """
        bean_views: list[BeanView] = []
        for func_name in dir(cls):
            if not func_name.startswith(cls.OBJECT_CREATION_IDENTIFIER):
                continue
            
            creation_func = getattr(cls, func_name)
            bean_name = creation_func.__annotations__[cls.RETURN_KEY].__name__
            final_creation_func = cls.construct_bean_creation_func(creation_func)
            view = BeanView(bean_name= bean_name, bean_creation_func=final_creation_func,bean= final_creation_func())
            logger.success(f"[BEAN CREATION UNDER {cls.__name__}] Found bean creation func: {view.bean_creation_func.__name__} with bean name: {view.bean_name}")
            bean_views.append(view)

        return bean_views
    
    @classmethod
    def construct_bean_creation_func(cls, bean_creation_func: Callable[..., Component]) -> Callable[..., Component]:
        properties_container = { 
            properties.get_name() : properties 
            for properties in _PropertiesLoader.optional_loaded_properties.values()
        }
        _kwargs = {}
        for param_key, param_cls in bean_creation_func.__annotations__.items():
            if param_key == cls.RETURN_KEY:
                continue
            properties_instance = properties_container.get(param_cls.__name__)
            _kwargs[param_key] = properties_instance
            
    
        return lambda: bean_creation_func(**_kwargs)
            
        
        
    
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

            

            