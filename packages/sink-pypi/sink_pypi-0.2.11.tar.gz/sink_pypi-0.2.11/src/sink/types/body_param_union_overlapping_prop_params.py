# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

__all__ = ["BodyParamUnionOverlappingPropParams", "ObjectWithFooProperty1", "ObjectWithFooProperty2"]


class ObjectWithFooProperty1(TypedDict, total=False):
    foo: Required[str]
    """FOO 1"""


class ObjectWithFooProperty2(TypedDict, total=False):
    foo: bool
    """FOO 2"""


BodyParamUnionOverlappingPropParams = Union[ObjectWithFooProperty1, ObjectWithFooProperty2]
