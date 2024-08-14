from pydantic import BaseModel


class ApplicationContextConfig(BaseModel):
    configuration_path: str
