import os
from typing import ClassVar
from loguru import logger
from pydantic import BaseModel
from py_spring.core.application.application_config import ApplicationConfigRepository
from py_spring.persistence.repositories.json_config_repository import (
    JsonConfigRepository,
)


class ApplicationProperties(BaseModel): ...


class ApplicationPropertiesRepository(JsonConfigRepository[ApplicationProperties]): ...


class ConfigFileTemplateGenerator:
    """
    Generates template configuration files for the application, including the app config and application properties files.
    The `ConfigFileTemplateGenerator` class is responsible for generating the template configuration files if they do not already exist in the target directory.
    It uses the `ApplicationConfigRepository` and `ApplicationPropertiesRepository` to load the template configurations and save them to the target directory.
    The `generate_app_config_file_template_if_not_exists` method checks if the app config file already exists in the target directory, and if not, generates the template file.
    The `generate_app_properties_file_template_if_not_exists` method checks if the application properties file already exists in the target directory, and if not, generates the template file.
    """

    APP_CONFIG_PATH: ClassVar[list[str]] = ["templates", "app-config.json"]
    APP_PROPERTIES_PATH: ClassVar[list[str]] = [
        "templates",
        "application-properties.json",
    ]

    def __init__(self, target_file_dir: str) -> None:
        self.target_file_dir = target_file_dir
        self.project_root = os.path.dirname(__file__)
        self.template_app_config_path = os.path.join(
            self.project_root, *self.APP_CONFIG_PATH
        )
        self.template_app_properties_path = os.path.join(
            self.project_root, *self.APP_PROPERTIES_PATH
        )
        self.app_config_repo = ApplicationConfigRepository(
            self.template_app_config_path
        )
        self.app_properties_repo = ApplicationPropertiesRepository(
            self.template_app_properties_path
        )

    def generate_app_config_file_template_if_not_exists(self) -> None:
        target_file = os.path.join(self.target_file_dir, self.APP_CONFIG_PATH[-1])

        if os.path.exists(target_file):
            logger.info(f"[APP CONFIG ALREADY EXISTS] {target_file} already exists")
            return
        self.app_config_repo.save_config_to_target_path(target_file)
        logger.success(
            f"[APP CONFIG GENERATED] App config file not exists, {target_file} generated"
        )

    def generate_app_properties_file_template_if_not_exists(self) -> None:
        target_file = os.path.join(self.target_file_dir, self.APP_PROPERTIES_PATH[-1])
        if os.path.exists(target_file):
            logger.info(f"[APP PROPERTIES ALREADY EXISTS] {target_file} already exists")
            return
        self.app_properties_repo.save_config_to_target_path(target_file)
        logger.success(
            f"[APP PROPERTIES GENERATED] App properties file not exists, {target_file} generated"
        )
