# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .._models import BaseModel

__all__ = ["ObjectWithAnyOfNullProperty", "Foo"]


class Foo(BaseModel):
    thing: Optional[str] = None


class ObjectWithAnyOfNullProperty(BaseModel):
    foo: Optional[Foo]
