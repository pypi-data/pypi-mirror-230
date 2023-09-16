# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Union
from typing_extensions import TypedDict

__all__ = ["QueryParamAnyOfParams"]


class QueryParamAnyOfParams(TypedDict, total=False):
    string_or_integer: Union[str, int]
