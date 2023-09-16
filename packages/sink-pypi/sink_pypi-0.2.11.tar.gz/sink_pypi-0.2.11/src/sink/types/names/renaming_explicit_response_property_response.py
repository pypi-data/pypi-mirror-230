# File generated from our OpenAPI spec by Stainless.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RenamingExplicitResponsePropertyResponse"]


class RenamingExplicitResponsePropertyResponse(BaseModel):
    name: str

    renamed: bool = FieldInfo(alias="original")
