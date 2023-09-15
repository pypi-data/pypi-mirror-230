# File generated from our OpenAPI spec by Stainless.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Version1_30NameCreateResponse"]


class Version1_30NameCreateResponse(BaseModel):
    version1_18: str = FieldInfo(alias="version_1_18")
