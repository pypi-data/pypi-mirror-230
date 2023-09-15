# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from ..types import shared_params

__all__ = ["TypeEnumsParams"]


class TypeEnumsParams(TypedDict, total=False):
    input_currency: Optional[shared_params.Currency]
    """This is my description for the Currency enum"""

    problematic_enum: Literal["123_FOO", "30%"]
