# File generated from our OpenAPI spec by Stainless.

import typing_extensions

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RenamingExplicitResponsePropertyResponse"]


class RenamingExplicitResponsePropertyResponse(BaseModel):
    name: str

    renamed: bool = FieldInfo(alias="original")

    @property
    @typing_extensions.deprecated("The renamed property should be used instead")
    def original(self) -> bool:
        return self.renamed
