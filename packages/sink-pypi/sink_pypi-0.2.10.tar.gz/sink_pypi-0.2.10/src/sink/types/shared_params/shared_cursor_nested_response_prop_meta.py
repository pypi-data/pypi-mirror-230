# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["SharedCursorNestedResponsePropMeta", "Pagination"]


class Pagination(TypedDict, total=False):
    cursor: Optional[str]
    """The cursor for the next page"""


class SharedCursorNestedResponsePropMeta(TypedDict, total=False):
    pagination: Required[Pagination]
