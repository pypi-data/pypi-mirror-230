# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TypeEnumTestsArrayUniqueValuesNumbersParams"]


class TypeEnumTestsArrayUniqueValuesNumbersParams(TypedDict, total=False):
    body: Required[List[Literal[5, 6, 7, 8]]]
