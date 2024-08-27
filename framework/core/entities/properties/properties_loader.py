import json
from typing import Optional, Type

import yaml

from framework.core.entities.properties.properties import Properties


class _PropertiesLoader:
    """
    Provides a utility class `_PropertiesLoader` to load and validate properties from a file.
    The `_PropertiesLoader` class is responsible for loading properties from a file, validating them against a set of known `Properties` classes, and providing access to the loaded properties.
    The class supports loading properties from JSON or YAML files, and raises appropriate errors if the file extension is unsupported or the properties keys are invalid.
    The `load_properties` method returns a dictionary of `Properties` instances, where the keys match the keys in the properties file.
    The `get_properties` method provides a way to retrieve a specific `Properties` instance by its key, if it has been previously loaded.
    """

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
