import importlib.util
from pathlib import Path
from typing import Iterable

from loguru import logger


def dynamically_import_modules(module_paths: Iterable[str], is_ignore_error: bool = True) -> None:
    for module_path in module_paths:
        file_path = Path(module_path).resolve()
        module_name = file_path.stem
        logger.info(f"[MODULE IMPORT] Import module path: {file_path}")
        # Create a module specification
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            logger.warning(
                f"[DYNAMICALLY MODULE IMPORT] Could not create spec for {module_name}"
            )
            continue

        # Create a new module based on the specification
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            logger.warning(
                f"[DYNAMICALLY MODULE IMPORT] No loader found for {module_name}"
            )
            continue

        # Execute the module in its own namespace
        try:
            spec.loader.exec_module(module)
            logger.success(
                f"[DYNAMICALLY MODULE IMPORT] Successfully imported {module_name}"
            )
        except Exception as error:
            logger.exception(error)
            if not is_ignore_error:
                raise error
