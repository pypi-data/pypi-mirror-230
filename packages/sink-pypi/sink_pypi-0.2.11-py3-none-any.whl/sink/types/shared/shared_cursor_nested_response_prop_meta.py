# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SharedCursorNestedResponsePropMeta", "Pagination"]


class Pagination(BaseModel):
    cursor: Optional[str] = None
    """The cursor for the next page"""


class SharedCursorNestedResponsePropMeta(BaseModel):
    pagination: Pagination
