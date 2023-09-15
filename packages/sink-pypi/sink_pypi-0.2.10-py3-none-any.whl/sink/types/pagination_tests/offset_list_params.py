# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["OffsetListParams"]


class OffsetListParams(TypedDict, total=False):
    limit: int

    offset: int
