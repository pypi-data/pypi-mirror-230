# File generated from our OpenAPI spec by Stainless.

from typing import List, Optional

from .parent import ChildModel
from ..._models import BaseModel

__all__ = ["ParentModelWithChildRef"]


class ParentModelWithChildRef(BaseModel):
    from_array: List[ChildModel]

    from_prop: ChildModel

    string_prop: Optional[str] = None
