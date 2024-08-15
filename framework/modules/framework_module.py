
from abc import ABC, abstractmethod
from typing import Iterable
from fastapi import FastAPI
from fastapi.routing import APIRouter


class _FrameworkModule(ABC):
    """
    Represents a module within the framework.
    
    The `_FrameworkModule` class is an abstract base class that defines the interface for a module within the framework.
    Subclasses of this class can be registered with the main FastAPI application to provide additional functionality.
    
    Modules should take responsibility for initializing any components they require. The framework will provide
    an instance of FastAPI during initialization. Each module is expected to configure and set up its own
    dependencies and components as needed.
    
    The `get_api_routers()` method returns an iterable of `APIRouter` instances that should be included in the main FastAPI application.
    The `enabled()` method is called after all modules have been initialized. It allows the module to perform any steps required for setting up the module
    This allows each module to define its own set of API endpoints.
    """
    def __init__(self, fastapi: FastAPI) -> None:
        pass

    @abstractmethod
    def get_api_routers(self) -> Iterable[APIRouter]:
        raise NotImplementedError()

    @abstractmethod
    def enabled(self) -> None:
        raise NotImplementedError()