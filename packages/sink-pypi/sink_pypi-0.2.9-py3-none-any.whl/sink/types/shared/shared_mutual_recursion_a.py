# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["SharedMutualRecursionA"]


class SharedMutualRecursionA(BaseModel):
    b: Optional[SharedMutualRecursionB] = None


from .shared_mutual_recursion_b import SharedMutualRecursionB

if PYDANTIC_V2:
    SharedMutualRecursionA.model_rebuild()
else:
    SharedMutualRecursionA.update_forward_refs()  # type: ignore
