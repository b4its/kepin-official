from __future__ import annotations
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class ApiSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class PaginatedResponse(ApiSchema, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def make_paginated(items: list[T], page: int, page_size: int, total: int) -> PaginatedResponse[T]:
    import math
    total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
