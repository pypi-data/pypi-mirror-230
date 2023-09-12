# File generated from our OpenAPI spec by Stainless.

from typing import Optional
from typing_extensions import Literal

from .shared import Currency
from .._models import BaseModel

__all__ = ["TypeEnumsResponse"]


class TypeEnumsResponse(BaseModel):
    currency: Optional[Currency]
    """This is my description for the Currency enum"""

    my_problematic_enum: Literal["123_FOO", "30%"]

    number_enum: Literal[200, 201, 404, 403]
