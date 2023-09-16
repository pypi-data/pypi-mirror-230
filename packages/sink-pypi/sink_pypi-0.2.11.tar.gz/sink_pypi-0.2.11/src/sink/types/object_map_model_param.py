# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["ObjectMapModelParam", "ObjectMapModelParamItem"]


class ObjectMapModelParamItem(TypedDict, total=False):
    foo: str


ObjectMapModelParam = Dict[str, ObjectMapModelParamItem]
