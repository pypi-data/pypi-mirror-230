# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from ..._models import BaseModel
from ..my_model import MyModel

__all__ = ["ObjectMultiplePropertiesSameModelResponse"]


class ObjectMultiplePropertiesSameModelResponse(BaseModel):
    required_prop: MyModel

    bar: Optional[MyModel] = None

    foo: Optional[MyModel] = None
