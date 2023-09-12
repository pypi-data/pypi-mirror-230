# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .level_one import LevelOne, AsyncLevelOne
from ..._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["DeeplyNested", "AsyncDeeplyNested"]


class DeeplyNested(SyncAPIResource):
    level_one: LevelOne

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.level_one = LevelOne(client)


class AsyncDeeplyNested(AsyncAPIResource):
    level_one: AsyncLevelOne

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.level_one = AsyncLevelOne(client)
