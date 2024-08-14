from typing import Optional, Type

from pydantic import BaseModel

from framework.core.application.context.application_context_config import ApplicationContextConfig
from framework.core.entities.bean_collection import BeanCollection, BeanConflictError, InvalidBeanError
from framework.core.entities.component import Component, ComponentScope
from loguru import logger

from framework.core.entities.configurations.configuration import Configuration
from framework.core.entities.controllers.rest_controller import RestController
from framework.core.entities.configurations.configuration_loader import _ConfigurationLoader

class ComponentNotFoundError(Exception): ...


class ApplicationContextView(BaseModel):
    config: ApplicationContextConfig
    component_cls_container: list[str]
    singleton_component_instance_container: list[str]


class ApplicationContext:
    """
    The `ApplicationContext` class is responsible for managing the lifecycle and dependencies of components in the application.
    It provides methods for registering components, retrieving component instances, and initializing the Inversion of Control (IoC) container.
    The `get_component()` method retrieves a component instance based on its class. For singleton components, it ensures that the same instance is returned on subsequent calls. For prototype components, it creates a new instance on each call.
    The `register_component()` method adds a component class to the container, making it available for retrieval.
    The `init_ioc_container()` method initializes the IoC container by creating singleton instances of all registered components.
    """
    def __init__(self, config: ApplicationContextConfig) -> None:
        self.primitive_types = (bool, str, int, float, type(None))

        self.config = config
        self.component_cls_container: dict[str, Type[Component]] = {}
        self.controller_cls_container: dict[str, Type[RestController]] = {}
        self.singleton_component_instance_container: dict[str, Component] = {}

        self.bean_collection_cls_container: dict[str, Type[BeanCollection]] = {}
        self.singleton_bean_instance_container: dict[str, object] = {}

        self.configuration_cls_container: dict[str, Type[Configuration]] = {}
        self.singleton_configuration_instance_container: dict[str, Configuration] = {}
        
    def _create_config_loader(self) -> _ConfigurationLoader:
        return _ConfigurationLoader(self.config.configuration_path, list(self.configuration_cls_container.values()))

    def as_view(self) -> ApplicationContextView:
        return ApplicationContextView(
            config=self.config,
            component_cls_container=list(self.component_cls_container.keys()),
            singleton_component_instance_container=list(self.singleton_component_instance_container.keys()),
        )


    def get_component(self, component_cls: Type[Component]) -> Optional[Component]:
        if not issubclass(component_cls, Component):
            return

        component_cls_name = component_cls.get_name()
        if component_cls_name not in self.component_cls_container:
            return
        
        scope = component_cls.get_scope()
        match scope:
            case ComponentScope.Singleton:
                optional_instance = self.singleton_component_instance_container.get(component_cls_name)
                return optional_instance
            
            case ComponentScope.Prototype:
                prototype_instance = component_cls()
                return prototype_instance
            
    def get_bean(self, object_cls: Type[object]) -> Optional[object]:
        bean_name = object_cls.__name__
        if bean_name not in self.singleton_bean_instance_container:
            return

        optional_instance = self.singleton_bean_instance_container.get(bean_name)
        return optional_instance
    
    def get_configuration(self, configuration_cls: Type[Configuration]) -> Optional[Configuration]:
        configuration_cls_name = configuration_cls.get_key()
        if configuration_cls_name not in self.configuration_cls_container:
            return
        optional_instance = self.singleton_configuration_instance_container.get(configuration_cls_name)
        return optional_instance
    
    def register_component(self, component_cls: Type[Component]) -> None:
        if not issubclass(component_cls, Component):
            raise TypeError(f"[COMPONENT REGISTRATION ERROR] Component: {component_cls} is not a subclass of Component")

        component_cls_name = component_cls.get_name()
        self.component_cls_container[component_cls_name] = component_cls


    def register_controller(self, controller_cls: Type[RestController]) -> None:
        if not issubclass(controller_cls, RestController):
            raise TypeError(f"[CONTROLLER REGISTRATION ERROR] Controller: {controller_cls} is not a subclass of RestController")
        
        controller_cls_name = controller_cls.get_name()
        self.controller_cls_container[controller_cls_name] = controller_cls

    def register_bean_collection(self, bean_cls: Type[BeanCollection]) -> None:
        if not issubclass(bean_cls, BeanCollection):
            raise TypeError(f"[BEAN COLLECTION REGISTRATION ERROR] BeanCollection: {bean_cls} is not a subclass of BeanCollection")

        bean_name = bean_cls.get_name()
        self.bean_collection_cls_container[bean_name] = bean_cls
        
    def register_configuration(self, configuration_cls: Type[Configuration]) -> None:
        if not issubclass(configuration_cls, Configuration):
            raise TypeError(f"[CONFIGURATION REGISTRATION ERROR] Configuration: {configuration_cls} is not a subclass of Configuration")
        configuration_name = configuration_cls.get_key()
        self.configuration_cls_container[configuration_name] = configuration_cls

    def get_controller_instances(self) -> list[RestController]:
        return [_cls() for _cls in self.controller_cls_container.values()]
    
    def get_singleton_component_instances(self) -> list[Component]:
        return [_cls for _cls in self.singleton_component_instance_container.values()]
    
    def get_singleton_bean_instances(self) -> list[object]:
        return [_cls for _cls in self.singleton_bean_instance_container.values()]

    def _init_ioc_container(self) -> None:
        """
        Initializes the IoC (Inversion of Control) container by creating singleton instances of all registered components.
        This method iterates through the registered component classes in the `component_cls_container` dictionary. 
        For each component class with a `Singleton` scope, it creates an instance of the component and stores it in the `singleton_component_instance_container` dictionary.
        This ensures that subsequent calls to `get_component()` for singleton components will return the same instance, as required by the Singleton design pattern.
        """
                
        
        for component_cls_name, component_cls in self.component_cls_container.items():
            if component_cls.get_scope() != ComponentScope.Singleton:
                continue
            logger.debug(f"[INITIALIZING SINGLETON COMPONENT] Init singleton component: {component_cls_name}")
            instance = component_cls()
            self.singleton_component_instance_container[component_cls_name] = instance

        # for bean
        for bean_collection_cls_name, bean_collection_cls in self.bean_collection_cls_container.items():
            logger.debug(f"[INITIALIZING SINGLETON BEAN] Init singleton bean: {bean_collection_cls_name}")
            collection = bean_collection_cls()
            bean_views = collection.scan_beans()
            for view in bean_views:
                if view.bean_name in self.singleton_bean_instance_container:
                    raise BeanConflictError(f"[BEAN CONFLICTS] Bean: {view.bean_name} already exists under collection: {collection.get_name()}")
                if not view.is_valid_bean():
                    raise InvalidBeanError(f"[INVALID BEAN] Bean name from bean creation func return type: {view.bean_name} does not match the bean object class name: {view.bean.__class__.__name__}")
                self.singleton_bean_instance_container[view.bean_name] = view.bean
                
                
        # for configuration
        config_loader = self._create_config_loader()
        for config_key, config_cls in self.configuration_cls_container.items():
            logger.debug(f"[INITIALIZING SINGLETON CONFIG] Init singleton configuration: {config_key}")
            configuration_instance_dict = config_loader.load_configs()
            self.singleton_configuration_instance_container[config_key] = configuration_instance_dict[config_key]


    def _inject_component_dependencies(self, entity: Type[Component | RestController]) -> None:
        for attr_name, annotated_entity_cls in entity.__annotations__.items():
            if annotated_entity_cls in self.primitive_types:
                logger.warning(
                    f"[DEPENDENCY INJECTION SKIPPED] Skip inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__} because it is primitive type"
                )
                continue
            
            if issubclass(annotated_entity_cls, Configuration):
                optional_config = self.get_configuration(annotated_entity_cls)
                setattr(entity, attr_name, optional_config)
                continue
                
            
            optional_component = self.get_component(annotated_entity_cls)
            if optional_component is not None:
                setattr(entity, attr_name, optional_component)
                logger.success(
                f"[DEPENDENCY INJECTION SUCCESS FROM COMPONENT CONTAINER] Inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__} singleton instance"
                )
                continue
            optional_bean = self.get_bean(annotated_entity_cls)

            if optional_bean is not None:
                setattr(entity, attr_name, optional_bean)
                logger.success(
                f"[DEPENDENCY INJECTION SUCCESS FROM BEAN COLLECTION CONTAINER] Inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__} singleton instance"
                )
                continue
            
            error_message = f"[DEPENDENCY INJECTION FAILED] Fail to inject dependency for attribute: {attr_name} with dependency: {annotated_entity_cls.__name__}, consider register such depency with Compoent decorator"
            logger.critical(error_message)
            raise ValueError(error_message)
            
            
    def inject_dependencies_for_component_container(self) -> None:
        for _component_cls_name, component_cls in self.component_cls_container.items():
            self._inject_component_dependencies(component_cls)


    def inject_dependencies_for_controller_container(self) -> None:
        for _controller_cls_name, controller_cls in self.controller_cls_container.items():
            self._inject_component_dependencies(controller_cls)

        