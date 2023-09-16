# File generated from our OpenAPI spec by Stainless.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["ResponseObjectWithAdditionalPropertiesPropResponse", "Foo"]


class Foo(BaseModel):
    bar: Optional[str] = None


class ResponseObjectWithAdditionalPropertiesPropResponse(BaseModel):
    foo: Dict[str, Foo]
