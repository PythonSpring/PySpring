from pydantic import BaseModel


class ApplicationContextConfig(BaseModel):
    """
    Represents the configuration for the application context, including the path to the properties file.
    """

    properties_path: str
