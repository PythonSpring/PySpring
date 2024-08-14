from typing import Type
from framework.core.entities.configurations.configuration import Configuration


class ConfigurationLoader:
    def __init__(self, config_path: str, configuration_classes: list[Type[Configuration]]) -> None:
        self.config_path = config_path
        self.configuration_classes = configuration_classes
    
    def load_classes(self) -> dict[str,Type[Configuration]]:
        return {
            _cls.get_key(): _cls 
            for _cls in self.configuration_classes
        } 
    
    def load_configs(self) -> list[Configuration]:
        ...