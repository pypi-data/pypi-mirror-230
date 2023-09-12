# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .._models import BaseModel

__all__ = ["ObjectSkippedProps"]


class ObjectSkippedProps(BaseModel):
    skipped_go: Optional[str] = None

    skipped_java: Optional[str] = None

    skipped_node: Optional[str] = None
