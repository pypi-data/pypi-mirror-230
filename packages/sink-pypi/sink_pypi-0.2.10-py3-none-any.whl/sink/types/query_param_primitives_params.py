# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["QueryParamPrimitivesParams"]


class QueryParamPrimitivesParams(TypedDict, total=False):
    boolean_param: bool

    integer_param: int

    number_param: float

    string_param: str
