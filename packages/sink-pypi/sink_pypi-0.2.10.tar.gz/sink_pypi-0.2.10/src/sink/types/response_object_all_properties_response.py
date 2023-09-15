# File generated from our OpenAPI spec by Stainless.

from typing import List
from typing_extensions import Literal

from .company import CompanyPayment
from .._models import BaseModel
from .simple_allof import SimpleAllof

__all__ = ["ResponseObjectAllPropertiesResponse"]


class ResponseObjectAllPropertiesResponse(BaseModel):
    allof: SimpleAllof

    b: bool

    e: Literal["active", "inactive", "pending"]

    i: int

    n: None

    object_array: List[CompanyPayment]

    primitive_array: List[str]

    s: str
