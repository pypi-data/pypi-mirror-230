from typing import ClassVar, Generic, TypeVar

from fastapi import status
from pydantic import BaseModel

T = TypeVar("T", bound="Result")
A = TypeVar("A")


class Error(BaseModel):
    message: str


class Result(Generic[A]):
    status_code: ClassVar[int]
    payload: A | Error | None = None

    def __init__(self, payload: A | Error | None = None) -> None:
        super().__init__()

        self.payload = payload

    def __bool__(self) -> bool:
        return not isinstance(self.payload, Error)


class Continue(Result[A]):
    status_code: ClassVar[int] = status.HTTP_100_CONTINUE

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class SwitchingProtocols(Result[A]):
    status_code: ClassVar[int] = status.HTTP_101_SWITCHING_PROTOCOLS

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Processing(Result[A]):
    status_code: ClassVar[int] = status.HTTP_102_PROCESSING

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class EarlyHints(Result[A]):
    status_code: ClassVar[int] = status.HTTP_103_EARLY_HINTS

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Ok(Result[A]):
    status_code: ClassVar[int] = status.HTTP_200_OK

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class Created(Result[A]):
    status_code: ClassVar[int] = status.HTTP_201_CREATED

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class Accepted(Result[A]):
    status_code: ClassVar[int] = status.HTTP_202_ACCEPTED

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class NonAuthoritativeInformation(Result[A]):
    status_code: ClassVar[int] = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class NoContent(Result[A]):
    status_code: ClassVar[int] = status.HTTP_204_NO_CONTENT

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class ResetContent(Result[A]):
    status_code: ClassVar[int] = status.HTTP_205_RESET_CONTENT

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class PartialContent(Result[A]):
    status_code: ClassVar[int] = status.HTTP_206_PARTIAL_CONTENT

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class MultiStatus(Result[A]):
    status_code: ClassVar[int] = status.HTTP_207_MULTI_STATUS

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class AlreadyReported(Result[A]):
    status_code: ClassVar[int] = status.HTTP_208_ALREADY_REPORTED

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class ImUsed(Result[A]):
    status_code: ClassVar[int] = status.HTTP_226_IM_USED

    def __init__(self, payload: A | None = None) -> None:
        super().__init__(payload=payload)


class MultipleChoices(Result[A]):
    status_code: ClassVar[int] = status.HTTP_300_MULTIPLE_CHOICES

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class MovedPermanently(Result[A]):
    status_code: ClassVar[int] = status.HTTP_301_MOVED_PERMANENTLY

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Found(Result[A]):
    status_code: ClassVar[int] = status.HTTP_302_FOUND

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class SeeOther(Result[A]):
    status_code: ClassVar[int] = status.HTTP_303_SEE_OTHER

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class NotModified(Result[A]):
    status_code: ClassVar[int] = status.HTTP_304_NOT_MODIFIED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class UseProxy(Result[A]):
    status_code: ClassVar[int] = status.HTTP_305_USE_PROXY

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Reserved(Result[A]):
    status_code: ClassVar[int] = status.HTTP_306_RESERVED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class TemporaryRedirect(Result[A]):
    status_code: ClassVar[int] = status.HTTP_307_TEMPORARY_REDIRECT

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class PermanentRedirect(Result[A]):
    status_code: ClassVar[int] = status.HTTP_308_PERMANENT_REDIRECT

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class BadRequest(Result[A]):
    status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Unauthorized(Result[A]):
    status_code: ClassVar[int] = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class PaymentRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_402_PAYMENT_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Forbidden(Result[A]):
    status_code: ClassVar[int] = status.HTTP_403_FORBIDDEN

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class NotFound(Result[A]):
    status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Method_NotAllowed(Result[A]):
    status_code: ClassVar[int] = status.HTTP_405_METHOD_NOT_ALLOWED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class NotAcceptable(Result[A]):
    status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Proxy_AuthenticationRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class RequestTimeout(Result[A]):
    status_code: ClassVar[int] = status.HTTP_408_REQUEST_TIMEOUT

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Conflict(Result[A]):
    status_code: ClassVar[int] = status.HTTP_409_CONFLICT

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Gone(Result[A]):
    status_code: ClassVar[int] = status.HTTP_410_GONE

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class LengthRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_411_LENGTH_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class PreconditionFailed(Result[A]):
    status_code: ClassVar[int] = status.HTTP_412_PRECONDITION_FAILED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Request_Entity_TooLarge(Result[A]):
    status_code: ClassVar[int] = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Request_Uri_TooLong(Result[A]):
    status_code: ClassVar[int] = status.HTTP_414_REQUEST_URI_TOO_LONG

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Unsupported_MediaType(Result[A]):
    status_code: ClassVar[int] = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Requested_Range_NotSatisfiable(Result[A]):
    status_code: ClassVar[int] = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class ExpectationFailed(Result[A]):
    status_code: ClassVar[int] = status.HTTP_417_EXPECTATION_FAILED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class ImA_Teapot(Result[A]):
    status_code: ClassVar[int] = status.HTTP_418_IM_A_TEAPOT

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class MisdirectedRequest(Result[A]):
    status_code: ClassVar[int] = status.HTTP_421_MISDIRECTED_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class UnprocessableEntity(Result[A]):
    status_code: ClassVar[int] = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Locked(Result[A]):
    status_code: ClassVar[int] = status.HTTP_423_LOCKED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class FailedDependency(Result[A]):
    status_code: ClassVar[int] = status.HTTP_424_FAILED_DEPENDENCY

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class TooEarly(Result[A]):
    status_code: ClassVar[int] = status.HTTP_425_TOO_EARLY

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class UpgradeRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_426_UPGRADE_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class PreconditionRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_428_PRECONDITION_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Too_ManyRequests(Result[A]):
    status_code: ClassVar[int] = status.HTTP_429_TOO_MANY_REQUESTS

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Request_Header_Fields_TooLarge(Result[A]):
    status_code: ClassVar[int] = status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Unavailable_For_LegalReasons(Result[A]):
    status_code: ClassVar[int] = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Internal_ServerError(Result[A]):
    status_code: ClassVar[int] = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class NotImplemented(Result[A]):
    status_code: ClassVar[int] = status.HTTP_501_NOT_IMPLEMENTED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class BadGateway(Result[A]):
    status_code: ClassVar[int] = status.HTTP_502_BAD_GATEWAY

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class ServiceUnavailable(Result[A]):
    status_code: ClassVar[int] = status.HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class GatewayTimeout(Result[A]):
    status_code: ClassVar[int] = status.HTTP_504_GATEWAY_TIMEOUT

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Http_Version_NotSupported(Result[A]):
    status_code: ClassVar[int] = status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class Variant_AlsoNegotiates(Result[A]):
    status_code: ClassVar[int] = status.HTTP_506_VARIANT_ALSO_NEGOTIATES

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class InsufficientStorage(Result[A]):
    status_code: ClassVar[int] = status.HTTP_507_INSUFFICIENT_STORAGE

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )


class LoopDetected(Result[A]):
    status_code: ClassVar[int] = status.HTTP_508_LOOP_DETECTED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class NotExtended(Result[A]):
    status_code: ClassVar[int] = status.HTTP_510_NOT_EXTENDED

    def __init__(self, message: str) -> None:
        super().__init__(payload=Error(message=message))


class Network_AuthenticationRequired(Result[A]):
    status_code: ClassVar[int] = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED

    def __init__(self, message: str) -> None:
        super().__init__(
            payload=Error(message=message),
        )
