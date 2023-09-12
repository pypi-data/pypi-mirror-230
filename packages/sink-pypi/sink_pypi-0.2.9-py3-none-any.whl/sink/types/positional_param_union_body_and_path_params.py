# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["PositionalParamUnionBodyAndPathParams"]


class PositionalParamUnionBodyAndPathParams(TypedDict, total=False):
    kind: Required[Literal["VIRTUAL", "PHYSICAL"]]
