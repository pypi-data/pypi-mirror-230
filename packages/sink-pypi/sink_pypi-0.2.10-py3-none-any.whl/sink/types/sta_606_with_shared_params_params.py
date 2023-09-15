# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..types import shared_params

__all__ = ["Sta606WithSharedParamsParams"]


class Sta606WithSharedParamsParams(TypedDict, total=False):
    bar: Required[shared_params.SimpleObject]

    foo: Required[str]
