
from enum import Enum
from typing import Type, final


class ComponentLifeCycle(Enum):
    Init = "initialization"
    Destruction = "destruction"

class ComponentScope(Enum):
    Singleton = "Singleton"
    Prototype = "Prototype"

class Component:
    class Config:
        scope: ComponentScope = ComponentScope.Singleton
    
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
    
    @classmethod
    def get_component_base(cls) -> "Type[Component]":
        return cls

    @classmethod
    def get_scope(cls) -> ComponentScope:
        return cls.Config.scope
    
    @classmethod
    def set_scope(cls, scope: ComponentScope) -> None:
        cls.Config.scope = scope

    
    def pre_initialize(self) -> None:
        """Hook method called before initialization"""
        pass

    def initialize(self) -> None:
        """Hook method called during initialization"""
        pass

    def post_initialize(self) -> None:
        """Hook method called after initialization"""
        pass

    def pre_destroy(self) -> None:
        """Hook method called before destruction"""
        pass

    def destroy(self) -> None:
        """Hook method called during destruction"""
        pass

    def post_destroy(self) -> None:
        """Hook method called after destruction"""
        pass

    @final
    def finish_initialization_cycle(self) -> None:
        self.pre_initialize()
        self.initialize()
        self.post_initialize()
    
    @final
    def finish_destruction_cycle(self) -> None:
        self.pre_destroy()
        self.destroy()
        self.post_destroy()


