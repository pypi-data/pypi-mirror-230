from typing import TypedDict


class TokenData(TypedDict):
    name: str
    token: str
    status: str
    created: str
    expires: str


class HttpResponse(TypedDict):
    statusCode: int
    message: str


class ErrorResponse(TypedDict):
    error: HttpResponse
