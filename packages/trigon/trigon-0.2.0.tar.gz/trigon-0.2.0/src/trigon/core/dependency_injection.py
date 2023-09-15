from typing import Any, Callable, Dict, Type, TypeVar

from lagom import Container as BaseContainer

from trigon.helpers.resolution import get_required_constructor_arguments

T = TypeVar("T")


class ContainerBuilder:
    def __init__(self) -> None:
        self.container = BaseContainer()

    def _resolve_constructor_arguments(self, dependency_type: Type[T]) -> Dict[str, Any]:
        arguments = get_required_constructor_arguments(dependency_type)

        resolved_arguments = {}
        for arg_name, arg_type in arguments.items():
            try:
                resolved_arguments[arg_name] = self.container[arg_type]
            except KeyError as e:
                msg = f"Missing dependency for argument '{arg_name}' of type '{arg_type}'"
                raise KeyError(
                    msg,
                ) from e

        return resolved_arguments

    def bind(self, dependency_type: Type[T], dependency: T | Callable[["ContainerBuilder"], T]):
        self.container[dependency_type] = dependency

        return self

    def singleton(self, dependency_type: Type[T]):
        resolved_arguments = self._resolve_constructor_arguments(dependency_type)

        self.container[dependency_type] = dependency_type(**resolved_arguments)

        return self

    def factory(self, dependency_type: Type[T]):
        resolved_arguments = self._resolve_constructor_arguments(dependency_type)

        def _(container: BaseContainer):
            return dependency_type(**resolved_arguments)

        self.container[dependency_type] = _

        return self

    def _build(self) -> BaseContainer:
        return self.container
