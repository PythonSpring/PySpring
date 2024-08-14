
from typing import Callable, Type
from framework.core.application.application_config import ApplicationConfigRepository
from framework.core.application.context.application_context import ApplicationContext
from framework.core.application.context.application_context_config import ApplicationContextConfig
from framework.core.entities.bean_collection import BeanCollection
from framework.core.entities.component import Component, ComponentLifeCycle
from framework.core.entities.controllers.rest_controller import RestController
from framework.core.utils.class_scanner import ClassScanner
from loguru import logger
from fastapi import FastAPI, APIRouter
import uvicorn

AppEntities = Component | RestController | BeanCollection

class Application:
    def __init__(self, app_config_path: str = "./app-config.json") -> None:
        logger.debug(f"[APP INIT] Initialize the app from config path: {app_config_path}")
        
        self.app_config_repo = ApplicationConfigRepository(app_config_path)
        self.app_config = self.app_config_repo.get_config()
        
        self.class_scanner = ClassScanner(self.app_config.app_src_target_dir)
        self.app_context_config = ApplicationContextConfig()
        self.app_context = ApplicationContext(self.app_context_config)
        self.fastapi = FastAPI()

        self.classes_with_handlers: dict[Type[AppEntities], Callable] = {
            Component: self._handle_register_component,
            RestController: self._handle_register_rest_controller,
            BeanCollection: self._handle_register_bean_collection,
        }

    
    def _scan_classes_for_project(self) -> None:
        self.class_scanner.scan_classes_under_directory()
        self.scanned_classes = self.class_scanner.get_classes()

    def _register_app_entities(self) -> None:
        for _cls in self.scanned_classes:
            for _target_cls, handler in self.classes_with_handlers.items():
                if not issubclass(_cls, _target_cls):
                    continue
                handler(_cls)

    def _handle_register_component(self, _cls: Type[Component]) -> None:
        self.app_context.register_component(_cls)

    def _handle_register_rest_controller(self, _cls: Type[RestController]) -> None:
        logger.debug(f"[REST CONTROLLER INIT] Register router for controller: {_cls.__name__}")
        self.app_context.register_controller(_cls)
        _cls.app = self.fastapi
        router_prefix = _cls.get_router_prefix()
        logger.debug(f"[REST CONTROLLER INIT] Register router with prefix: {router_prefix}")
        _cls.router = APIRouter(prefix= router_prefix)

    
    def _handle_register_bean_collection(self, _cls: Type[BeanCollection]) -> None:
        logger.debug(f"[BEAN COLLECTION INIT] Register bean collection: {_cls.__name__}")
        self.app_context.register_bean_collection(_cls)
    

    def __init_app(self) -> None:
        self._scan_classes_for_project()
        self._register_app_entities()
        self.app_context._init_ioc_container()
        self.app_context.inject_dependencies_for_component_container()
        # after injecting all deps, lifecycle (init) can be called
        self._handle_singleton_components_life_cycle(ComponentLifeCycle.Init)
        self.app_context.inject_dependencies_for_controller_container()


    def _handle_singleton_components_life_cycle(self, life_cycle: ComponentLifeCycle) -> None:
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
        uvicorn.run(self.fastapi, host = self.app_config.server_config.host, port= self.app_config.server_config.port)

    def run(self) -> None:
        try:
            self.__init_app()
            self.__init_controllers()
            self.__run_server()
        finally:
            self._handle_singleton_components_life_cycle(ComponentLifeCycle.Destruction)


    