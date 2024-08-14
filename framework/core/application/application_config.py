from pydantic import BaseModel

from framework.core.repositories.json_config_repository import JsonConfigRepository


class ServerConfig(BaseModel):
    host: str
    port: int

class ApplicationConfig(BaseModel):
    app_src_target_dir: str
    server_config: ServerConfig
    sqlalchemy_database_uri: str
    properties_file_path: str
    


class ApplicationConfigRepository(JsonConfigRepository[ApplicationConfig]): ...