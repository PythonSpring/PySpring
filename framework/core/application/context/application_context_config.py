from pydantic import BaseModel


class ApplicationContextConfig(BaseModel):
    properties_path: str
