# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .payments import Payments, AsyncPayments
from ..._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["CompanyResource", "AsyncCompanyResource"]


class CompanyResource(SyncAPIResource):
    payments: Payments

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.payments = Payments(client)


class AsyncCompanyResource(AsyncAPIResource):
    payments: AsyncPayments

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.payments = AsyncPayments(client)
