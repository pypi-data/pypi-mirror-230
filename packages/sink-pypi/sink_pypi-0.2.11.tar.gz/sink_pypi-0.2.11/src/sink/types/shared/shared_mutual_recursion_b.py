# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["SharedMutualRecursionB"]


class SharedMutualRecursionB(BaseModel):
    a: Optional[SharedMutualRecursionA] = None


from .shared_mutual_recursion_a import SharedMutualRecursionA

if PYDANTIC_V2:
    SharedMutualRecursionB.model_rebuild()
else:
    SharedMutualRecursionB.update_forward_refs()  # type: ignore
