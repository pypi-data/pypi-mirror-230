# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .string_map_model_param import StringMapModelParam

__all__ = ["BodyParamStringMapModelRefParams"]


class BodyParamStringMapModelRefParams(TypedDict, total=False):
    model_ref: Required[StringMapModelParam]

    name: Required[str]
