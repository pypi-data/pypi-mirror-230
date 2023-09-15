# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

from ..types import shared_params

__all__ = ["BodyParamTopLevelArrayParams"]


class BodyParamTopLevelArrayParams(TypedDict, total=False):
    items: Required[List[shared_params.BasicSharedModelObject]]
