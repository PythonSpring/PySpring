from typing import Mapping, Type
from py_spring.core.application.commons import AppEntities
from py_spring.core.application.context.application_context import ApplicationContext
from py_spring.core.utils import check_type_hints_for_class


class ApplicationContextTypeChecker:
    def __init__(
        self, app_context: ApplicationContext, skip_class_attrs: list[str]
    ) -> None:
        self.app_context = app_context
        self.skip_class_attrs = skip_class_attrs

    def check_type_hints_for_context(self, ctx: ApplicationContext) -> None:
        containers: list[Mapping[str, Type[AppEntities]]] = [
            ctx.component_cls_container,
            ctx.controller_cls_container,
            ctx.bean_collection_cls_container,
            ctx.properties_cls_container,
        ]
        for container in containers:
            for _cls in container.values():
                check_type_hints_for_class(_cls, skip_attrs=self.skip_class_attrs)
