# File generated from our OpenAPI spec by Stainless.

import builtins
import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["NamePropertiesCommonConflictsResponse"]


class NamePropertiesCommonConflictsResponse(BaseModel):
    bool: builtins.bool

    bool2: builtins.bool = FieldInfo(alias="bool_2")
    """
    In certain languages the type declaration for this prop can shadow the `bool`
    property declaration.
    """

    date: datetime.date
    """This shadows the stdlib `datetime.date` type in Python & causes type errors."""

    date2: datetime.date = FieldInfo(alias="date_2")
    """
    In certain languages the type declaration for this prop can shadow the `date`
    property declaration.
    """

    float: builtins.float

    float2: builtins.float = FieldInfo(alias="float_2")
    """
    In certain languages the type declaration for this prop can shadow the `float`
    property declaration.
    """

    int: builtins.int

    int2: builtins.int = FieldInfo(alias="int_2")
    """
    In certain languages the type declaration for this prop can shadow the `int`
    property declaration.
    """
