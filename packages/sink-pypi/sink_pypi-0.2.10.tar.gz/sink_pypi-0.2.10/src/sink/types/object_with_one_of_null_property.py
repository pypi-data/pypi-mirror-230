# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .._models import BaseModel

__all__ = ["ObjectWithOneOfNullProperty", "Foo"]


class Foo(BaseModel):
    item: Optional[str] = None


class ObjectWithOneOfNullProperty(BaseModel):
    foo: Optional[Foo]
