# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["BodyParamWithDefaultBodyParamRequiredParams"]


class BodyParamWithDefaultBodyParamRequiredParams(TypedDict, total=False):
    normal_param: Required[bool]

    my_version_body_param: str
