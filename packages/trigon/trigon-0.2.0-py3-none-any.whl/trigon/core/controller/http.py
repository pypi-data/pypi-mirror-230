from http.client import responses as description_per_status_code
from typing import Callable, Type, TypeVar

from trigon.core.controller.result import Error, Result

T = TypeVar("T")


def status(
    result_type: Type[Result[T]],
    model: Type[T] = Error,
    description: str | None = None,
) -> Callable[..., Result[T]]:
    if description is None:
        description = description_per_status_code[result_type.status_code]

    def _(endpoint: Callable[..., Result[T]]):
        if not hasattr(endpoint, "_responses"):
            endpoint._responses = {}
            endpoint._status_code = result_type.status_code

        endpoint._responses[result_type.status_code] = {
            "model": model,
            "description": description,
        }

        return endpoint

    return _
