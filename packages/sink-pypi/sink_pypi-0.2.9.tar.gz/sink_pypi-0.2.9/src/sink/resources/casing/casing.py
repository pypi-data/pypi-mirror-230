# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .eeoc import EEOCResource, AsyncEEOCResource
from ..._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Casing", "AsyncCasing"]


class Casing(SyncAPIResource):
    eeoc: EEOCResource

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.eeoc = EEOCResource(client)


class AsyncCasing(AsyncAPIResource):
    eeoc: AsyncEEOCResource

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.eeoc = AsyncEEOCResource(client)
