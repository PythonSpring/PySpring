import importlib.util
from inspect import isclass
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Type, get_type_hints

from loguru import logger


def dynamically_import_modules(
    module_paths: Iterable[str],
    is_ignore_error: bool = True,
    target_subclasses: Iterable[Type[object]] = [],
) -> set[Type[object]]:
    """
    Dynamically imports modules from the specified file paths.

    Args:
        module_paths (Iterable[str]): The file paths of the modules to import.
        is_ignore_error (bool, optional): Whether to ignore any errors that occur during the import process. Defaults to True.

    Raises:
        Exception: If an error occurs during the import process and `is_ignore_error` is False.
    """
    all_loaded_classes: list[Type[object]] = []

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

        logger.info(f"[DYNAMICALLY MODULE IMPORT] Import module: {module_name}")
        try:
            spec.loader.exec_module(module)
            logger.success(
                f"[DYNAMICALLY MODULE IMPORT] Successfully imported {module_name}"
            )
        except Exception as error:
            logger.warning(error)
            if not is_ignore_error:
                raise error

        loaded_classes = []
        for attr in dir(module):
            obj = getattr(module, attr)
            if attr.startswith("__"):
                continue
            if not isclass(obj):
                continue
            loaded_classes.append(obj)
        all_loaded_classes.extend(loaded_classes)

    returned_target_classes: set[Type[object]] = set()
    for target_cls in target_subclasses:
        for loaded_class in all_loaded_classes:
            if loaded_class in target_subclasses:
                continue
            if issubclass(loaded_class, target_cls):
                returned_target_classes.add(loaded_class)

    return returned_target_classes


class TypeHintsNotProvidedError(Exception): ...

def checking_type_hints_for_callable(func: Callable[..., Any]) -> None:
    RETURN_ID = "return"
    
    argument_count = func.__code__.co_argcount + 1 # plue one is for return type, return type is not included in co_argcount
    annotations = func.__annotations__
    args_type_hints = get_type_hints(func)
    full_type_hints = {**annotations, **args_type_hints}

    if RETURN_ID not in full_type_hints:
        raise TypeHintsNotProvidedError("Type hints for 'return type' not provided for the function")
    if argument_count == 0:
        return 
    if len(full_type_hints) == 0:
        raise TypeHintsNotProvidedError(f"Type hints not provided for the function, number of arguments: {argument_count} and type hints: {full_type_hints}")
    
    if len(full_type_hints) != argument_count:
        raise TypeHintsNotProvidedError(f"Number of type hints does not match the number of arguments in the function: {full_type_hints}, number of arguments: {argument_count}")