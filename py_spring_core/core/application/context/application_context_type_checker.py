from typing import Any, Iterable, Mapping, Type

from loguru import logger
from py_spring_core.core.application.commons import AppEntities
from py_spring_core.core.application.context.application_context import ApplicationContext
from py_spring_core.core.utils import TypeHintError, check_type_hints_for_class


class ApplicationContextTypeChecker:
    def __init__(
        self, app_context: ApplicationContext, 
        skip_class_attrs: list[str], 
        target_classes: Iterable[Type[Any]], 
        skipped_classes: Iterable[Type[Any]]
    ) -> None:
        self.app_context = app_context
        self.skip_class_attrs = skip_class_attrs
        self.target_classes = target_classes
        self.skipped_classes = skipped_classes


    def check_type_hints_for_context(self, ctx: ApplicationContext) -> None:
        containers: list[Mapping[str, Type[AppEntities]]] = [
            ctx.component_cls_container,
            ctx.controller_cls_container,
            ctx.bean_collection_cls_container,
            ctx.properties_cls_container,
        ]
        for container in containers:
            for _cls in container.values():
                if issubclass(_cls, tuple(self.skipped_classes)):
                    continue
                if _cls not in self.target_classes:
                    try:
                        check_type_hints_for_class(_cls, skip_attrs=self.skip_class_attrs)
                    except TypeHintError as error:
                        logger.warning(f"Type hint error for class {_cls.__name__}: {error}")
                        raise error
                    except NameError as error:
                        ...