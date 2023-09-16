# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .import_ import ImportResource, AsyncImportResource
from ...._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ...._client import Sink, AsyncSink

__all__ = ["ReservedNames", "AsyncReservedNames"]


class ReservedNames(SyncAPIResource):
    import_: ImportResource

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.import_ = ImportResource(client)


class AsyncReservedNames(AsyncAPIResource):
    import_: AsyncImportResource

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.import_ = AsyncImportResource(client)
