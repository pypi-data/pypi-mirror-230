# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DuplicateQueryAndBodyParams"]


class DuplicateQueryAndBodyParams(TypedDict, total=False):
    query_id: Required[Annotated[str, PropertyInfo(alias="id")]]
    """Query param description"""

    body_id: Required[Annotated[str, PropertyInfo(alias="id")]]
    """Body param description"""
