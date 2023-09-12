# File generated from our OpenAPI spec by Stainless.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ArrayObjectItemsResponse", "ArrayObjectItemsResponseItem"]


class ArrayObjectItemsResponseItem(BaseModel):
    nice_foo: Optional[str] = None


ArrayObjectItemsResponse = List[ArrayObjectItemsResponseItem]
