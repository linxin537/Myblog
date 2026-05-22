from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: list[T] | None = None
    pagination: PaginationMeta | None = None


def success_response(data: Any = None, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data}


def error_response(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}
