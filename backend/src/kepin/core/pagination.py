from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar
from uuid import UUID as UuidType
from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import ColumnProperty

T = TypeVar("T")


def _to_serializable(v: Any) -> Any:
    if isinstance(v, (UuidType, Decimal, datetime)):
        return str(v)
    return v


class ApiSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
        coerce_numbers_to_str=True,
    )

    @model_validator(mode='before')
    @classmethod
    def _coerce_from_orm(cls, data: Any) -> Any:
        if hasattr(data, '__table__'):
            d: dict[str, Any] = {}
            mapper = sa_inspect(type(data))
            for col in mapper.columns:
                prop = mapper.get_property_by_column(col)
                if isinstance(prop, ColumnProperty):
                    key = prop.key
                else:
                    key = col.name
                d[col.name] = _to_serializable(getattr(data, key))
            return d
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (UuidType, Decimal, datetime)):
                    data[k] = str(v)
        return data


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
