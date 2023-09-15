# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from ...._models import BaseModel

__all__ = ["ChildModel", "InlineObject"]


class InlineObject(BaseModel):
    foo: Optional[float] = None


class ChildModel(BaseModel):
    inline_object: InlineObject

    name: str
