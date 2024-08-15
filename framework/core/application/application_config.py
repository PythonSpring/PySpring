from typing import Optional
from pydantic import BaseModel, Field

from framework.persistence.repositories.json_config_repository import JsonConfigRepository


class ServerConfig(BaseModel):
    host: str
    port: int

class ApplicationConfig(BaseModel):
    app_src_target_dir: str
    server_config: ServerConfig
    sqlalchemy_database_uri: str = Field(default="sqlite:///:memory:")
    properties_file_path: str
    model_file_postfix_patterns: list[str] = Field(default= ["models.py"])
    
class ApplicationConfigRepository(JsonConfigRepository[ApplicationConfig]): ...