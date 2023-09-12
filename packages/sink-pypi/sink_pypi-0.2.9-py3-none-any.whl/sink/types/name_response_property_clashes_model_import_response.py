# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .balance import Balance
from .._models import BaseModel

__all__ = ["NameResponsePropertyClashesModelImportResponse"]


class NameResponsePropertyClashesModelImportResponse(BaseModel):
    balance: Balance

    optional_balance: Optional[Balance] = None
