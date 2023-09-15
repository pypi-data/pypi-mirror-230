# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["CursorListParams"]


class CursorListParams(TypedDict, total=False):
    cursor: Optional[str]

    limit: int
