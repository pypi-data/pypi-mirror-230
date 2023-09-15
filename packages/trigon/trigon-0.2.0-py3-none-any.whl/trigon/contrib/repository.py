from typing import Any


class Repository:
    class RepositoryException(Exception):
        @property
        def message(self):
            return str(self)

    class NotFoundException(RepositoryException):
        def __init__(self, model: type, **kwargs: dict[str, Any]) -> None:
            super().__init__()

            self._model_name = model.__name__.title()
            self._kwargs = kwargs

        def __str__(self) -> str:
            kwargs_str = ", ".join(f"{key} {value}" for key, value in self._kwargs.items())

            return f"There is no {self._model_name} with {kwargs_str}"

    class ConflictException(RepositoryException):
        def __init__(self, model: type, **kwargs: dict[str, Any]) -> None:
            super().__init__()

            self._model_name = model.__name__.title()
            self._kwargs = kwargs

        def __str__(self) -> str:
            kwargs_str = ", ".join(f"{key} {value}" for key, value in self._kwargs.items())

            return f"{self._model_name} with {kwargs_str} already exists"
