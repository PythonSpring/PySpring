import json
from typing import Type
import yaml
from framework.core.entities.configurations.configuration import Configuration


class _ConfigurationLoader:
    def __init__(self, config_path: str, configuration_classes: list[Type[Configuration]]) -> None:
        self.config_path = config_path
        self.configuration_classes = configuration_classes
        self.configuration_class_map = self._load_classes_as_map()

        self.extension_loader_lookup = {
            "json": json.loads,
            "yaml": yaml.load,
            "yml": yaml.load,
        }
    
    def _load_classes_as_map(self) -> dict[str,Type[Configuration]]:
        return {
            _cls.get_key(): _cls 
            for _cls in self.configuration_classes
        } 
    
    def _load_config_dict(self) -> dict[str, dict]:
        file_extension = self.config_path.split(".")[-1]
        with open(self.config_path, "r") as config_file:
            for extension, loader_func in self.extension_loader_lookup.items():
                file_content = config_file.read()
                if file_extension == extension:
                    return loader_func(file_content)
                
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    def load_configs(self) -> dict[str,Configuration]:
        config_dict = self._load_config_dict()
        configs:dict[str,Configuration] = {}
        for key, value in config_dict.items():
            if key not in self.configuration_class_map.keys():
                raise ValueError(f"[INVALID CONFIG KEY] Invalid configuration key: {key}, please enter one of the following [{','.join(self.configuration_class_map.keys())}]")
            config_cls = self.configuration_class_map[key]
            configs[key] = config_cls.model_validate(value)
        return configs