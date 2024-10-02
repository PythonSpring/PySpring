import importlib.util
import inspect
from pathlib import Path
from typing import Any, Callable, Iterable, Type, get_type_hints

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
            if not inspect.isclass(obj):
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


class TypeHintError(Exception): ...


def check_type_hints_for_callable(func: Callable[..., Any]) -> None:
    RETURN_ID = "return"
    func_qualname_list = func.__qualname__.split(".")
    is_class_callable = True if len(func_qualname_list) == 2 else False
    class_name = func_qualname_list[0] if is_class_callable else ""

    func_name = func.__name__
    args_type_hints = get_type_hints(func)
    arg_type = inspect.getargs(func.__code__)
    code_path = inspect.getsourcefile(func)
    if RETURN_ID not in args_type_hints:
        raise TypeHintError(
            f"Type hints for 'return type' not provided for the function: {class_name}.{func_name}, path: {code_path}"
        )

    # plue one is for return type, return type is not included in co_argcount if it is a simple function,
    # for member functions, self is included in co_varnames, but not in type hints, so plus 0
    arguments = arg_type.args
    argument_count = len(arguments)
    if argument_count == 0:
        return
    if len(args_type_hints) == 0:
        raise TypeHintError(
            f"Type hints not provided for the function: {class_name}.{func_name}, arguments: {arguments}, current type hints: {args_type_hints}, path: {code_path}"
        )

    if len(args_type_hints) != argument_count:
        missing_type_hints_args = [
            arg for arg in arguments if arg not in args_type_hints and arg != "self"
        ]
        if len(missing_type_hints_args) == 0:
            return
        raise TypeHintError(
            f"Type hints not fully provided: {class_name}.{func_name}, arguments: {arguments}, current type hints: {args_type_hints}, missingg type hints: {','.join(missing_type_hints_args)}, path: {code_path}"
        )


def check_type_hints_for_class(_cls: Type[Any], skip_attrs: list[str] = list()) -> None:
    for attr in dir(_cls):
        if attr in skip_attrs:
            continue
        if attr.startswith("__"):
            continue
        attr_obj = getattr(_cls, attr)
        if not callable(attr_obj):
            continue
        if not hasattr(attr_obj, "__annotations__"):
            continue
        check_type_hints_for_callable(attr_obj)
