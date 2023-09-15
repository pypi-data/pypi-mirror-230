from typing import Type

from trigon.core.controller import Controller
from trigon.core.dependency_injection import ContainerBuilder
from trigon.core.event_handler import EventHandler
from trigon.core.middleware import Middleware


class Plugin:
    def register_dependencies(self, container: ContainerBuilder) -> ContainerBuilder:
        return container

    def get_controllers(self) -> list[Type[Controller]]:
        return []

    def get_middlewares(self) -> list[Type[Middleware]]:
        return []

    def get_event_handlers(self) -> list[EventHandler]:
        return []
