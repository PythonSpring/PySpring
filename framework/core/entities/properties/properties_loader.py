import json
from typing import Any, Optional, Type

import yaml

from framework.core.entities.properties.properties import Properties


class _PropertiesLoader:
    optional_loaded_properties: dict[str, Properties] = {}

    def __init__(
        self, properties_path: str, properties_classes: list[Type[Properties]]
    ) -> None:
        self.properties_path = properties_path
        self.properties_classes = properties_classes
        self.properties_class_map = self._load_classes_as_map()

        self.extension_loader_lookup = {
            "json": json.loads,
            "yaml": yaml.load,
            "yml": yaml.load,
        }

    def _load_classes_as_map(self) -> dict[str, Type[Properties]]:
        return {_cls.get_key(): _cls for _cls in self.properties_classes}

    def _load_properties_dict(self) -> dict[str, dict]:
        file_extension = self.properties_path.split(".")[-1]
        with open(self.properties_path, "r") as properties_file:
            for extension, loader_func in self.extension_loader_lookup.items():
                if file_extension != extension:
                    continue

                file_content = properties_file.read()
                return loader_func(file_content)
        raise ValueError(f"Unsupported file extension: {file_extension}")

    def load_properties(self) -> dict[str, Properties]:
        properties_dict = self._load_properties_dict()
        properties: dict[str, Properties] = {}
        for key, value in properties_dict.items():
            if key not in self.properties_class_map.keys():
                raise ValueError(
                    f"[INVALID PROPERTIES KEY] Invalid properties key: {key}, please enter one of the following [{','.join(self.properties_class_map.keys())}]"
                )
            properties_cls = self.properties_class_map[key]
            properties[key] = properties_cls.model_validate(value)
        return properties

    @classmethod
    def get_properties(cls, _key: str) -> Optional[Properties]:
        if cls.optional_loaded_properties is None:
            raise ValueError("[PROPERTIES NOT LOADED] Properties not loaded yet")
        return cls.optional_loaded_properties.get(_key)
