from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound="ServiceResult")
A = TypeVar("A")


class Service:
    pass


class ServiceError(BaseModel):
    message: str


class ServiceResult(Generic[A]):
    status_code: ClassVar[int]
    payload: A | ServiceError | None = None

    def __init__(self, payload: A | ServiceError | None = None) -> None:
        super().__init__()

        self.payload = payload

    def __bool__(self) -> bool:
        return not isinstance(self.payload, ServiceError)
