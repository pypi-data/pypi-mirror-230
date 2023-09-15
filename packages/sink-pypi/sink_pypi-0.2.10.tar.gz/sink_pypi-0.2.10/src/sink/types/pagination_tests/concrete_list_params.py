# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ConcreteListParams"]


class ConcreteListParams(TypedDict, total=False):
    my_cursor: Required[str]

    limit: int
