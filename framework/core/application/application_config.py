
from pydantic import BaseModel, Field

from framework.persistence.repositories.json_config_repository import (
    JsonConfigRepository,
)


class ServerConfig(BaseModel):
    """
    Represents the configuration for the application server.
    
    Attributes:
        host: The host address for the server.
        port: The port number for the server.
    """
        
    host: str
    port: int


class ApplicationConfig(BaseModel):
    """
    Represents the configuration for the application.
    
    Attributes:
        app_src_target_dir: The directory where the application source code is located.
        server_config: The configuration for the application server.
        sqlalchemy_database_uri: The URI for the SQLAlchemy database connection.
        properties_file_path: The file path for the application properties.
        model_file_postfix_patterns: A list of file name patterns for model (for table creation) files.
    """
        
    app_src_target_dir: str
    server_config: ServerConfig
    sqlalchemy_database_uri: str = Field(default="sqlite:///:memory:")
    properties_file_path: str
    model_file_postfix_patterns: list[str] = Field(default=["models.py"])


class ApplicationConfigRepository(JsonConfigRepository[ApplicationConfig]): 
    """
    Represents a repository for managing the application configuration, which is stored in a JSON file.
    """
    ...
