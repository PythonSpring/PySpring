import pytest
from fastapi import APIRouter, FastAPI

from py_spring_core.core.entities.controllers.rest_controller import RestController


class TestRestController:
    @pytest.fixture
    def app(self) -> FastAPI:
        return FastAPI()

    @pytest.fixture
    def router(self) -> APIRouter:
        return APIRouter()

    @pytest.fixture
    def test_controller(self, app: FastAPI, router: APIRouter) -> RestController:
        class TestController(RestController):
            def register_routes(self):
                self.router.add_api_route("/test", lambda: "test")

        TestController.app = app
        TestController.router = router

        return TestController()

    def test_register_routes_successfully(self, test_controller: RestController):
        test_controller.register_routes()
        assert len(test_controller.router.routes) == 1
