# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TypeEnumTestsArrayUniqueValues2ValuesParams"]


class TypeEnumTestsArrayUniqueValues2ValuesParams(TypedDict, total=False):
    body: Required[List[Literal["USD", "GBP"]]]
