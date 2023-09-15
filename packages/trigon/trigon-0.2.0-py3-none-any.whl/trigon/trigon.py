"""A batteries-included python web framework."""


from types import ModuleType
from typing import Any, Callable, Dict, Optional, Type, Union

from fastapi import APIRouter, FastAPI

from trigon.contrib.plugins import PluginBuilder
from trigon.core.controller import Controller
from trigon.core.dependency_injection import ContainerBuilder
from trigon.core.event_handler import EventHandler
from trigon.core.logging import LoggerBuilder
from trigon.core.middleware import Middleware
from trigon.core.settings import Settings
from trigon.helpers.resolution import get_constructor_annotations, get_types


class trigon(FastAPI):
    def __init__(
        self,
        title: str = "trigon",
        description: str = "A batteries-included python web framework",
        version: str = "1.0.0",
        contact: Optional[Dict[str, Union[str, Any]]] = None,
        docs_url: str = "/",
    ) -> None:
        super().__init__(
            title=title,
            description=description,
            version=version,
            contact=contact,
            docs_url=docs_url,
        )

        self.settings_types: list[Type[Settings]] = []
        self.container_builder: Callable[[ContainerBuilder], ContainerBuilder] | None = None
        self.logger_builder: Callable[[LoggerBuilder], LoggerBuilder] | None = None
        self.plugin_builder: Callable[[PluginBuilder], PluginBuilder] | None = None
        self.controller_types: list[Type[Controller]] = []
        self.middleware_types: list[Type[Middleware]] = []
        self.event_handler_types: list[EventHandler] = []

    def register_settings(self, *settings_types: Type[Settings]) -> "trigon":
        self.settings_types = settings_types

        return self

    def build_container(self, container_builder: Callable[[ContainerBuilder], ContainerBuilder]):
        self.container_builder = container_builder

        return self

    def load_plugins(self, plugin_builder: Callable[[PluginBuilder], PluginBuilder]) -> "trigon":
        self.plugin_builder = plugin_builder

        return self

    def configure_logging(self, logger_builder: Callable[[LoggerBuilder], LoggerBuilder]):
        self.logger_builder = logger_builder

        return self

    def register_controllers(self, *controller_types: Type[Controller]) -> "trigon":
        if controller_types:
            self.controller_types = controller_types

        return self

    def discover_controllers(self, module: ModuleType) -> "trigon":
        return self.register_controllers(*get_types(module, Controller))

    def register_middlewares(self, *middleware_types: Type[Middleware]) -> "trigon":
        if middleware_types:
            self.middleware_types = middleware_types

        return self

    def register_event_handlers(self, *event_handler_types: EventHandler) -> "trigon":
        if event_handler_types:
            self.event_handler_types = event_handler_types

        return self

    def build(self) -> "trigon":
        self.container = ContainerBuilder()

        self.container.singleton(Settings.create_combined_model(*self.settings_types))

        for setting_type in self.settings_types:
            self.container.singleton(setting_type)

        if self.plugin_builder is not None:
            for plugin in self.plugin_builder(PluginBuilder())._build():
                self.container = plugin.register_dependencies(self.container)
                self.register_event_handlers(*plugin.get_event_handlers())
                self.register_middlewares(*plugin.get_middlewares())

        if self.container_builder is not None:
            self.container = self.container_builder(self.container)._build()
        else:
            self.container = self.container._build()

        def _(controller_type: Type[Controller]):
            annotations = get_constructor_annotations(controller_type)

            resolved_arguments = {}
            for arg_name, arg_type in annotations.items():
                try:
                    resolved_arguments[arg_name] = self.container[arg_type]
                except KeyError as e:
                    msg = f"Missing dependency for argument '{arg_name}' of type '{arg_type}'"
                    raise KeyError(
                        msg,
                    ) from e

            return controller_type(**resolved_arguments)

        api = APIRouter(prefix="/api")

        for controller in map(_, self.controller_types):
            api.include_router(controller.as_view())

        self.include_router(api)

        if self.logger_builder is not None:
            self.logger_builder = self.logger_builder(LoggerBuilder())

        if self.logger_builder.middleware_type is not None:
            self.middleware_types.extend([self.logger_builder.middleware_type])

        for middleware_type in self.middleware_types:
            self.add_middleware(middleware_type)

        for event_handler in self.event_handler_types:
            self.add_event_handler(event_handler.event_type, event_handler)

        return self
