from inspect import isclass
from typing import Callable, Mapping, Optional, Type, TypeVar

from loguru import logger
from pydantic import BaseModel

from py_spring.core.application.context.application_context_config import (
    ApplicationContextConfig,
)
from py_spring.core.entities.bean_collection import (
    BeanCollection,
    BeanConflictError,
    InvalidBeanError,
)
from py_spring.core.entities.component import Component, ComponentScope
from py_spring.core.entities.controllers.rest_controller import RestController
from py_spring.core.entities.properties.properties import Properties
from py_spring.core.entities.properties.properties_loader import _PropertiesLoader


AppEntities = Component | RestController | BeanCollection | Properties


T = TypeVar("T", bound=AppEntities)


class ComponentNotFoundError(Exception): ...


class ApplicationContextView(BaseModel):
    config: ApplicationContextConfig
    component_cls_container: list[str]
    singleton_component_instance_container: list[str]


class ApplicationContext:
    """
    The `ApplicationContext` class is the main entry point for the application's context management.
    It is responsible for:
        1. Registering and managing the lifecycle of components, controllers, bean collections, and properties.
        2. Providing methods to retrieve instances of registered components, beans, and properties.
        3. Initializing the Inversion of Control (IoC) container by creating singleton instances of registered components.
        4. Injecting dependencies for registered components and controllers.
    The `ApplicationContext` class is designed to follow the Singleton design pattern, ensuring that there is a single instance of the application context throughout the application's lifetime.
    """

    def __init__(self, config: ApplicationContextConfig) -> None:
        self.primitive_types = (bool, str, int, float, type(None))

        self.config = config
        self.component_cls_container: dict[str, Type[Component]] = {}
        self.controller_cls_container: dict[str, Type[RestController]] = {}
        self.singleton_component_instance_container: dict[str, Component] = {}

        self.bean_collection_cls_container: dict[str, Type[BeanCollection]] = {}
        self.singleton_bean_instance_container: dict[str, object] = {}

        self.properties_cls_container: dict[str, Type[Properties]] = {}
        self.singleton_properties_instance_container: dict[str, Properties] = {}

    def _create_properties_loader(self) -> _PropertiesLoader:
        return _PropertiesLoader(
            self.config.properties_path, list(self.properties_cls_container.values())
        )

    def as_view(self) -> ApplicationContextView:
        return ApplicationContextView(
            config=self.config,
            component_cls_container=list(self.component_cls_container.keys()),
            singleton_component_instance_container=list(
                self.singleton_component_instance_container.keys()
            ),
        )

    def get_component(self, component_cls: Type[T]) -> Optional[T]:
        if not issubclass(component_cls, Component):
            return

        component_cls_name = component_cls.get_name()
        if component_cls_name not in self.component_cls_container:
            return

        scope = component_cls.get_scope()
        match scope:
            case ComponentScope.Singleton:
                optional_instance = self.singleton_component_instance_container.get(
                    component_cls_name
                )
                return optional_instance  # type: ignore

            case ComponentScope.Prototype:
                prototype_instance = component_cls()
                return prototype_instance

    def get_bean(self, object_cls: Type[T]) -> Optional[T]:
        bean_name = object_cls.__name__
        if bean_name not in self.singleton_bean_instance_container:
            return

        optional_instance = self.singleton_bean_instance_container.get(bean_name)
        return optional_instance  # type: ignore

    def get_properties(self, properties_cls: Type[Properties]) -> Optional[Properties]:
        properties_cls_name = properties_cls.get_key()
        if properties_cls_name not in self.properties_cls_container:
            return
        optional_instance = self.singleton_properties_instance_container.get(
            properties_cls_name
        )
        return optional_instance

    def register_component(self, component_cls: Type[Component]) -> None:
        if not issubclass(component_cls, Component):
            raise TypeError(
                f"[COMPONENT REGISTRATION ERROR] Component: {component_cls} is not a subclass of Component"
            )

        component_cls_name = component_cls.get_name()
        self.component_cls_container[component_cls_name] = component_cls

    def register_controller(self, controller_cls: Type[RestController]) -> None:
        if not issubclass(controller_cls, RestController):
            raise TypeError(
                f"[CONTROLLER REGISTRATION ERROR] Controller: {controller_cls} is not a subclass of RestController"
            )

        controller_cls_name = controller_cls.get_name()
        self.controller_cls_container[controller_cls_name] = controller_cls

    def register_bean_collection(self, bean_cls: Type[BeanCollection]) -> None:
        if not issubclass(bean_cls, BeanCollection):
            raise TypeError(
                f"[BEAN COLLECTION REGISTRATION ERROR] BeanCollection: {bean_cls} is not a subclass of BeanCollection"
            )

        bean_name = bean_cls.get_name()
        self.bean_collection_cls_container[bean_name] = bean_cls

    def register_properties(self, properties_cls: Type[Properties]) -> None:
        if not issubclass(properties_cls, Properties):
            raise TypeError(
                f"[PROPERTIES REGISTRATION ERROR] Properties: {properties_cls} is not a subclass of Properties"
            )
        properties_name = properties_cls.get_key()
        self.properties_cls_container[properties_name] = properties_cls

    def get_controller_instances(self) -> list[RestController]:
        return [_cls() for _cls in self.controller_cls_container.values()]

    def get_singleton_component_instances(self) -> list[Component]:
        return [_cls for _cls in self.singleton_component_instance_container.values()]

    def get_singleton_bean_instances(self) -> list[object]:
        return [_cls for _cls in self.singleton_bean_instance_container.values()]

    def load_properties(self) -> None:
        properties_loader = self._create_properties_loader()
        properties_instance_dict = properties_loader.load_properties()
        for properties_key, properties_cls in self.properties_cls_container.items():
            logger.debug(
                f"[INITIALIZING SINGLETON PROPERTIES] Init singleton properties: {properties_key}"
            )
            optional_properties = properties_instance_dict.get(properties_key)
            if optional_properties is None:
                raise TypeError(
                    f"[PROPERTIES INITIALIZATION ERROR] Properties: {properties_key} is not found in properties file for class: {properties_cls.get_name()} with key: {properties_cls.get_key()}"
                )
            self.singleton_properties_instance_container[properties_key] = (
                optional_properties
            )
        _PropertiesLoader.optional_loaded_properties = (
            self.singleton_properties_instance_container
        )

    def init_ioc_container(self) -> None:
        """
        Initializes the IoC (Inversion of Control) container by creating singleton instances of all registered components.
        This method iterates through the registered component classes in the `component_cls_container` dictionary.
        For each component class with a `Singleton` scope, it creates an instance of the component and stores it in the `singleton_component_instance_container` dictionary.
        This ensures that subsequent calls to `get_component()` for singleton components will return the same instance, as required by the Singleton design pattern.
        """

        # for Components
        for component_cls_name, component_cls in self.component_cls_container.items():
            if component_cls.get_scope() != ComponentScope.Singleton:
                continue
            logger.debug(
                f"[INITIALIZING SINGLETON COMPONENT] Init singleton component: {component_cls_name}"
            )
            instance = component_cls()
            self.singleton_component_instance_container[component_cls_name] = instance

        # for Bean
        for (
            bean_collection_cls_name,
            bean_collection_cls,
        ) in self.bean_collection_cls_container.items():
            logger.debug(
                f"[INITIALIZING SINGLETON BEAN] Init singleton bean: {bean_collection_cls_name}"
            )
            collection = bean_collection_cls()
            # before injecting_bean_collection deps and scanning beans, make sure properties is loaded in _PropertiesLoader by calling load_properties inside Application class
            self._inject_dependencies_for_bean_collection(bean_collection_cls)
            bean_views = collection.scan_beans()
            for view in bean_views:
                if view.bean_name in self.singleton_bean_instance_container:
                    raise BeanConflictError(
                        f"[BEAN CONFLICTS] Bean: {view.bean_name} already exists under collection: {collection.get_name()}"
                    )
                if not view.is_valid_bean():
                    raise InvalidBeanError(
                        f"[INVALID BEAN] Bean name from bean creation func return type: {view.bean_name} does not match the bean object class name: {view.bean.__class__.__name__}"
                    )
                self.singleton_bean_instance_container[view.bean_name] = view.bean

    def _inject_entity_dependencies(self, entity: Type[AppEntities]) -> None:
        for attr_name, annotated_entity_cls in entity.__annotations__.items():
            is_injected: bool = False
            if annotated_entity_cls in self.primitive_types:
                logger.warning(
                    f"[DEPENDENCY INJECTION SKIPPED] Skip inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__} because it is primitive type"
                )
                continue

            if not isclass(annotated_entity_cls):
                continue

            if issubclass(annotated_entity_cls, Properties):
                optional_properties = self.get_properties(annotated_entity_cls)
                if optional_properties is None:
                    raise TypeError(
                        f"[PROPERTIES INJECTION ERROR] Properties: {annotated_entity_cls.get_name()} is not found in properties file for class: {annotated_entity_cls.get_name()} with key: {annotated_entity_cls.get_key()}"
                    )
                setattr(entity, attr_name, optional_properties)
                continue

            entity_getters: list[Callable] = [self.get_component, self.get_bean]

            for getter in entity_getters:
                optional_entity = getter(annotated_entity_cls)
                if optional_entity is not None:
                    setattr(entity, attr_name, optional_entity)
                    is_injected = True
                    break

            if is_injected:
                logger.success(
                    f"[DEPENDENCY INJECTION SUCCESS FROM COMPONENT CONTAINER] Inject dependency for {annotated_entity_cls.__name__} in attribute: {attr_name} with dependency: {annotated_entity_cls.__name__} singleton instance"
                )
                continue

            error_message = f"[DEPENDENCY INJECTION FAILED] Fail to inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__}, consider register such depency with Compoent decorator"
            logger.critical(error_message)
            raise ValueError(error_message)

    def _inject_dependencies_for_bean_collection(
        self, bean_collection_cls: Type[BeanCollection]
    ) -> None:
        logger.info(
            f"[BEAN COLLECTION DEPENDENCY INJECTION] Injecting dependencies for {bean_collection_cls.get_name()}"
        )
        self._inject_entity_dependencies(bean_collection_cls)

    def inject_dependencies_for_app_entities(self) -> None:
        containers: list[Mapping[str, Type[AppEntities]]] = [
            self.component_cls_container,
            self.controller_cls_container,
        ]

        for container in containers:
            for _cls_name, _cls in container.items():
                self._inject_entity_dependencies(_cls)