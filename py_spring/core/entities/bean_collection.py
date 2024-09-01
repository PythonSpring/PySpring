from typing import Callable

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from py_spring.core.entities.component import Component
from py_spring.core.entities.properties.properties_loader import _PropertiesLoader


class BeanView(BaseModel):
    """
    The `BeanView` class represents a single bean within a `BeanCollection`.
    It contains information about the bean, such as its name and the function used to create it.

    The `is_valid_bean()` method checks whether the bean name matches the name of the bean's class.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    bean_creation_func: Callable[..., object] = Field(exclude=True)
    bean_name: str
    bean: object

    def is_valid_bean(self) -> bool:
        return self.bean_name == self.bean.__class__.__name__


class BeanConflictError(Exception):
    """
    Raised when there is a conflict between beans in a `BeanCollection`.
    """

    ...


class InvalidBeanError(Exception):
    """
    Raised when a bean in a `BeanCollection` is invalid, such as when the bean name does not match the name of the bean's class.
    """

    ...


class BeanCollection:
    """
    Provides a `BeanCollection` class that scans and manages a collection of beans (components) within a class.

    The `BeanCollection` class has the following key features:

    - `scan_beans()`: Scans the current class for bean creation functions and returns a list of `BeanView` objects, which contain information about each bean.
    - `construct_bean_creation_func()`: Constructs a bean creation function that automatically injects any required properties based on the bean creation function's type annotations.
    - `get_name()`: Returns the name of the `BeanCollection` class.

    The `BeanView` class represents a single bean within the collection and contains information about the bean, such as its name and the function used to create it.

    The `BeanConflictError` and `InvalidBeanError` exceptions are used to handle errors related to bean creation and management.
    """

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
            view = BeanView(
                bean_name=bean_name,
                bean_creation_func=final_creation_func,
                bean=final_creation_func(),
            )
            logger.success(
                f"[BEAN CREATION UNDER {cls.__name__}] Found bean creation func: {view.bean_creation_func.__name__} with bean name: {view.bean_name}"
            )
            bean_views.append(view)

        return bean_views

    @classmethod
    def construct_bean_creation_func(
        cls, bean_creation_func: Callable[..., Component]
    ) -> Callable[..., Component]:
        properties_container = {
            properties.get_name(): properties
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
