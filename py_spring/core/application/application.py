import inspect
from typing import Callable, Iterable, Type, cast

import uvicorn
from fastapi import APIRouter, FastAPI
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError as SqlAlehemyInvalidRequestError
from sqlmodel import SQLModel

import py_spring.core.utils as core_utils
from py_spring.core.application.application_config import ApplicationConfigRepository
from py_spring.core.application.context.application_context import AppEntities, ApplicationContext
from py_spring.core.application.context.application_context_config import (
    ApplicationContextConfig,
)
from py_spring.core.entities.bean_collection import BeanCollection
from py_spring.core.entities.component import Component, ComponentLifeCycle
from py_spring.core.entities.controllers.rest_controller import RestController
from py_spring.core.entities.properties.properties import Properties
from py_spring.core.util_classes.class_scanner import ClassScanner
from py_spring.core.util_classes.file_path_scanner import FilePathScanner
from py_spring.modules.framework_module import _FrameworkModule
from py_spring.persistence.core.py_spring_model import PySpringModel



class ApplicationFileGroups(BaseModel):
    class_files: set[str]
    model_files: set[str]


class Application:
    """
    The `Application` class is the main entry point for the application.
    It is responsible for initializing the application, registering application entities, and running the FastAPI server.

    The class performs the following tasks:
    - Loads the application configuration from a JSON file.
    - Creates a SQLAlchemy engine based on the configuration.
    - Scans the application source directory for Python files and groups them into class files and model files.
    - Scans the class files to find all classes that implement the `AppEntities` interface (Component, RestController, BeanCollection, Properties).
    - Registers the found application entities with the `ApplicationContext`.
    - Imports all model modules (table classes) and creates all SQLModel tables.
    - Initializes the FastAPI application and registers all REST controllers.
    - Runs the FastAPI server using Uvicorn.
    """

    PY_FILE_EXTENSION = ".py"

    def __init__(
        self,
        app_config_path: str = "./app-config.json",
        module_classes: Iterable[Type[_FrameworkModule]] = list(),
    ) -> None:
        logger.debug(
            f"[APP INIT] Initialize the app from config path: {app_config_path}"
        )

        self.module_classes = module_classes
        self._model_classes: set[type[object]] = set()
        self.app_config_repo = ApplicationConfigRepository(app_config_path)
        self.app_config = self.app_config_repo.get_config()
        self.sql_engine = create_engine(
            url=self.app_config.sqlalchemy_database_uri, echo=True
        )
        self.file_path_scanner = FilePathScanner(
            target_dir=self.app_config.app_src_target_dir,
            target_extensions=[self.PY_FILE_EXTENSION],
        )
        self.target_dir_absolute_file_paths = (
            self.file_path_scanner.scan_file_paths_under_directory()
        )
        self.app_file_groups = self._group_file_paths(
            self.target_dir_absolute_file_paths
        )
        self.app_class_scanner = ClassScanner(self.app_file_groups.class_files)
        self.app_context_config = ApplicationContextConfig(
            properties_path=self.app_config.properties_file_path
        )
        self.app_context = ApplicationContext(config=self.app_context_config)
        self.fastapi = FastAPI()

        self.classes_with_handlers: dict[Type[AppEntities], Callable] = {
            Component: self._handle_register_component,
            RestController: self._handle_register_rest_controller,
            BeanCollection: self._handle_register_bean_collection,
            Properties: self._handle_register_properties,
        }

    def _group_file_paths(self, files: Iterable[str]) -> ApplicationFileGroups:
        class_files: set[str] = set()
        model_files: set[str] = set()

        for file in files:
            py_file_name = self._get_file_base_name(file)
            if py_file_name in self.app_config.model_file_postfix_patterns:
                model_files.add(file)
            if file not in model_files:
                class_files.add(file)
        return ApplicationFileGroups(class_files=class_files, model_files=model_files)

    def _import_model_modules(self) -> None:
        logger.info(
            f"[SQLMODEL TABLE MODEL IMPORT] Import all models: {self.app_file_groups.model_files}"
        )

        def import_func_wrapper() -> set[type[object]]:
            return core_utils.dynamically_import_modules(
                self.app_file_groups.model_files,
                is_ignore_error=False,
                target_subclasses=[PySpringModel, SQLModel],
            )

        try:
            self._model_classes = import_func_wrapper()
        except SqlAlehemyInvalidRequestError as error:
            logger.warning(
                f"[ERROR ADVISE] Encounter {error.__class__.__name__} when importing model classes."
            )
            logger.error(
                f"[SQLMODEL TABLE MODEL IMPORT FAILED] Failed to import model modules: {error}"
            )
            self._model_classes = self._get_pyspring_model_inheritors()

    def _is_from_model_file(self, cls: Type[object]) -> bool:
        try:
            source_file_name = inspect.getsourcefile(cls)
        except TypeError as error:
            logger.warning(
                f"[CHECK MODEL FILE] Failed to get source file name for class: {cls.__name__}, largely due to built-in classes.\n Actual error: {error}"
            )
            return False
        if source_file_name is None:
            return False
        py_file_name = self._get_file_base_name(source_file_name)  # e.g., models.py
        return py_file_name in self.app_config.model_file_postfix_patterns

    def _get_file_base_name(self, file_path: str) -> str:
        return file_path.split("/")[-1]

    def _get_pyspring_model_inheritors(self) -> set[Type[object]]:
        # use dict to store all models, use a session to check if all models are mapped
        class_name_with_class_map: dict[str, Type[object]] = {}
        for _cls in set(PySpringModel.__subclasses__()):
            if _cls.__name__ in class_name_with_class_map:
                continue
            if not self._is_from_model_file(_cls):
                logger.warning(
                    f"[SQLMODEL TABLE MODEL IMPORT] {_cls.__name__} is not from model file, skip it."
                )
                continue

            class_name_with_class_map[_cls.__name__] = _cls

        return set(class_name_with_class_map.values())

    def _create_all_tables(self) -> None:
        logger.success(
            f"[SQLMODEL TABLE CREATION] Create all SQLModel tables, engine url: {self.sql_engine.url}, tables: {', '.join(SQLModel.metadata.tables.keys())}"
        )
        SQLModel.metadata.create_all(self.sql_engine)
        logger.success(
            f"[SQLMODEL TABLE MODEL IMPORT] Get model classes from PySpringModel inheritors: {', '.join([_cls.__name__ for _cls in self._model_classes])}"
        )

        PySpringModel.set_engine(self.sql_engine)
        PySpringModel.set_models(
            cast(list[Type[PySpringModel]], list(self._model_classes))
        )
        PySpringModel.set_metadata(SQLModel.metadata)

    def _scan_classes_for_project(self) -> None:
        self.app_class_scanner.scan_classes_for_file_paths()
        self.scanned_classes = self.app_class_scanner.get_classes()

    def _register_app_entities(self) -> None:
        for _cls in self.scanned_classes:
            for _target_cls, handler in self.classes_with_handlers.items():
                if not issubclass(_cls, _target_cls):
                    continue
                handler(_cls)

    def _handle_register_component(self, _cls: Type[Component]) -> None:
        self.app_context.register_component(_cls)

    def _handle_register_rest_controller(self, _cls: Type[RestController]) -> None:
        logger.debug(
            f"[REST CONTROLLER INIT] Register router for controller: {_cls.__name__}"
        )
        self.app_context.register_controller(_cls)
        _cls.app = self.fastapi
        router_prefix = _cls.get_router_prefix()
        logger.debug(
            f"[REST CONTROLLER INIT] Register router with prefix: {router_prefix}"
        )
        _cls.router = APIRouter(prefix=router_prefix)

    def _handle_register_bean_collection(self, _cls: Type[BeanCollection]) -> None:
        logger.debug(
            f"[BEAN COLLECTION INIT] Register bean collection: {_cls.__name__}"
        )
        self.app_context.register_bean_collection(_cls)

    def _handle_register_properties(self, _cls: Type[Properties]) -> None:
        logger.debug(f"[PROPERTIES INIT] Register properties: {_cls.__name__}")
        self.app_context.register_properties(_cls)

    def __init_app(self) -> None:
        self._scan_classes_for_project()
        self._import_model_modules()
        self._create_all_tables()
        self._register_app_entities()
        self.app_context._load_properties()
        self.app_context._init_ioc_container()
        self.app_context.inject_dependencies_for_app_entities()
        # after injecting all deps, lifecycle (init) can be called
        self._handle_singleton_components_life_cycle(ComponentLifeCycle.Init)

    def _handle_singleton_components_life_cycle(
        self, life_cycle: ComponentLifeCycle
    ) -> None:
        components = self.app_context.get_singleton_component_instances()
        for component in components:
            match life_cycle:
                case ComponentLifeCycle.Init:
                    component.finish_initialization_cycle()
                case ComponentLifeCycle.Destruction:
                    component.finish_destruction_cycle()

    def __init_controllers(self) -> None:
        controllers = self.app_context.get_controller_instances()
        for controller in controllers:
            controller.register_routes()
            router = controller.get_router()
            self.fastapi.include_router(router)
            controller.register_middlewares()

    def __run_server(self) -> None:
        uvicorn.run(
            self.fastapi,
            host=self.app_config.server_config.host,
            port=self.app_config.server_config.port,
        )

    def __enable_modules(self) -> None:
        for module_cls in self.module_classes:
            module = module_cls(self.fastapi)
            logger.info(f"[MODULE ENABLED] Enable module: {module_cls.__name__}")
            for router in module.get_api_routers():
                self.fastapi.include_router(router)
            module.enabled()

    def run(self) -> None:
        try:
            self.__init_app()
            self.__init_controllers()
            self.__enable_modules()
            if self.app_config.server_config.enabled:
                self.__run_server()
        finally:
            self._handle_singleton_components_life_cycle(ComponentLifeCycle.Destruction)
