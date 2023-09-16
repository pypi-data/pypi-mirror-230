# File generated from our OpenAPI spec by Stainless.



from ..._models import BaseModel
from .simple_object import SimpleObject

__all__ = ["ObjectWithChildRef"]


class ObjectWithChildRef(BaseModel):
    bar: SimpleObject

    foo: str
