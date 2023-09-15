from functools import wraps
from typing import Callable, Type, TypeVar, get_args, get_origin, get_type_hints

from fastapi import HTTPException

from trigon.core.controller.result import Result

T = TypeVar("T")


def get_unwrapped_return_type(endpoint: Callable[..., Result[T]]) -> Type:
    type_hints = get_type_hints(endpoint)

    return_type = type_hints.get("return", None)

    generic_type = get_origin(return_type)

    if generic_type is None or generic_type is not Result:
        msg = "Invalid return type"
        raise TypeError(msg)

    type_args = get_args(return_type)

    if len(type_args) != 1:
        msg = "Invalid return type"
        raise TypeError(msg)

    unwrapped_return_type = type_args[0]
    if unwrapped_return_type is type(None):
        return None

    return unwrapped_return_type


def get(prefix: str):
    def _(endpoint: Callable[..., Result[T]]):
        endpoint._http_method = "GET"
        endpoint._prefix = prefix

        @wraps(endpoint)
        async def __(*args, **kwargs):
            result = await endpoint(*args, **kwargs)

            if not result:
                raise HTTPException(status_code=result.status_code, detail=result.payload.message)

            return result.payload

        __.__annotations__["return"] = get_unwrapped_return_type(endpoint)

        return __

    return _


def post(prefix: str):
    def _(endpoint: Callable[..., Result[T]]):
        endpoint._http_method = "POST"
        endpoint._prefix = prefix

        @wraps(endpoint)
        async def __(*args, **kwargs):
            result = await endpoint(*args, **kwargs)

            if not result:
                raise HTTPException(status_code=result.status_code, detail=result.error.message)

            return result.payload

        __.__annotations__["return"] = get_unwrapped_return_type(endpoint)

        return __

    return _


def delete(prefix: str):
    def _(endpoint: Callable[..., Result[T]]):
        endpoint._http_method = "DELETE"
        endpoint._prefix = prefix

        @wraps(endpoint)
        async def __(*args, **kwargs):
            result = await endpoint(*args, **kwargs)

            if not result:
                raise HTTPException(status_code=result.status_code, detail=result.error.message)

            return result.payload

        __.__annotations__["return"] = get_unwrapped_return_type(endpoint)

        return __

    return _
