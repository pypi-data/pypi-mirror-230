import inspect
import itertools
import pkgutil
from collections.abc import Iterable
from types import ModuleType
from typing import Any, TypeVar

T = TypeVar("T", bound=type)


def get_modules(parent_module: ModuleType, public_only: bool = True) -> Iterable[ModuleType]:
    modules: list[ModuleType] = []

    for loader, module_name, _ in pkgutil.walk_packages(parent_module.__path__):
        if module_name.startswith("_") and public_only:
            continue

        module = loader.find_module(module_name).load_module(module_name)

        modules.append(module)

    return sorted(modules, key=lambda module: module.__name__)


def get_types(parent_module: ModuleType, Type_: type[T]) -> list[type[T]]:
    def is_subclass_defined_in_module(Type___: type[T], module: ModuleType) -> bool:
        return (
            inspect.getmodule(Type___) is module
            and inspect.isclass(Type___)
            and issubclass(Type___, Type_)
            and not issubclass(Type_, Type___)
        )

    _types: list[type[T]] = []

    for module in get_modules(parent_module):
        for name, Type__ in inspect.getmembers(
            module,
            lambda Type___: is_subclass_defined_in_module(Type___, module),
        ):
            if name in _types:
                msg = f"class `{name}` is defined multiple times."
                raise KeyError(msg)

            _types.append(Type__)

    return _types


def get_constructor_arguments(Type_: T) -> dict[str, dict[str, Any]]:
    arguments = {
        parameter.name: {
            "annotation": parameter.annotation,
            "default": parameter.default,
            "kind": parameter.kind,
        }
        for parameter in itertools.islice(
            inspect.signature(Type_.__init__).parameters.values(),
            1,
            None,
        )
    }

    if (
        {"args", "kwargs"}.issubset(arguments.keys())
        and arguments.get("args", {}).get("annotation", inspect._empty) is inspect._empty
        and arguments.get("kwargs", {}).get("annotation", inspect._empty) is inspect._empty
    ):
        return {}

    return arguments


def get_constructor_annotations(Type_: T) -> dict[str, Any]:
    return {
        name: metadata["annotation"] for name, metadata in get_constructor_arguments(Type_).items()
    }


def get_required_constructor_arguments(Type_: T) -> dict[str, Any]:
    arguments = {}
    for name, metadata in get_constructor_arguments(Type_).items():
        if (
            metadata["kind"] == inspect._ParameterKind.KEYWORD_ONLY
            or metadata["kind"] == inspect._ParameterKind.VAR_KEYWORD
            or (
                metadata["kind"] == inspect._ParameterKind.POSITIONAL_OR_KEYWORD
                and metadata["default"] is not inspect._empty
            )
        ):
            continue

        arguments[name] = metadata["annotation"]

    return arguments
