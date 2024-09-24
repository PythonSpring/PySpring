
from dataclasses import field, dataclass
from typing import Type

from py_spring.core.entities.bean_collection import BeanCollection
from py_spring.core.entities.component import Component
from py_spring.core.entities.properties.properties import Properties
from py_spring.persistence.core.py_spring_model import PySpringModel


@dataclass
class EntityProvider:
    component_classes: list[Type[Component]] = field(default_factory= list)
    bean_collection_classes: list[Type[BeanCollection]] = field(default_factory= list)
    properties_classes: list[Type[Properties]] = field(default_factory= list)
    model_classes: list[Type[PySpringModel]] = field(default_factory= list)


    def get_entities(self) -> list[Type[object]]:
        return [*self.component_classes, 
                *self.bean_collection_classes, 
                *self.properties_classes
                ]
    
    def get_models(self) -> list[Type[PySpringModel]]:
        return self.model_classes