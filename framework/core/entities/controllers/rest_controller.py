from fastapi import APIRouter, FastAPI


class RestController:
    app: FastAPI
    router: APIRouter

    class Config:
        prefix: str = ""

    def register_routes(self) -> None: ...

    def register_middlewares(self) -> None: ...

    def get_router(self) -> APIRouter:
        return self.router

    @classmethod
    def get_router_prefix(cls) -> str:
        return cls.Config.prefix

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
