
from dataclasses import field, dataclass
from typing import Optional, Type

from py_spring.core.application.commons import AppEntities
from py_spring.core.application.context.application_context import ApplicationContext
from py_spring.core.entities.bean_collection import BeanCollection
from py_spring.core.entities.component import Component
from py_spring.core.entities.controllers.rest_controller import RestController
from py_spring.core.entities.properties.properties import Properties

@dataclass
class EntityProvider:
    component_classes: list[Type[Component]] = field(default_factory= list)
    bean_collection_classes: list[Type[BeanCollection]] = field(default_factory= list)
    properties_classes: list[Type[Properties]] = field(default_factory= list)
    rest_controller_classes: list[Type[RestController]] = field(default_factory= list)
    depends_on: list[Type[AppEntities]] = field(default_factory= list)
    app_context: Optional[ApplicationContext] = None

    def get_entities(self) -> list[Type[object]]:
        return [*self.component_classes, 
                *self.bean_collection_classes, 
                *self.properties_classes,
                *self.rest_controller_classes
                ]
    
    def set_context(self, app_context: ApplicationContext) -> None:
        self.app_context = app_context

    def provider_init(self) -> None: ...