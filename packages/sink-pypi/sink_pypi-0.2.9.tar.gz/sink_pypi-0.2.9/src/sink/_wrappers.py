# File generated from our OpenAPI spec by Stainless.

from typing import Generic, TypeVar

from ._models import GenericModel

__all__ = ["DataWrapper", "ItemsWrapper"]

_T = TypeVar("_T")


class DataWrapper(GenericModel, Generic[_T]):
    data: _T


class ItemsWrapper(GenericModel, Generic[_T]):
    items: _T
