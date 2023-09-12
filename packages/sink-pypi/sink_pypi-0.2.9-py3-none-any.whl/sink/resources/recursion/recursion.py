# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._resource import SyncAPIResource, AsyncAPIResource
from .shared_responses import SharedResponses, AsyncSharedResponses

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Recursion", "AsyncRecursion"]


class Recursion(SyncAPIResource):
    shared_responses: SharedResponses

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.shared_responses = SharedResponses(client)


class AsyncRecursion(AsyncAPIResource):
    shared_responses: AsyncSharedResponses

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.shared_responses = AsyncSharedResponses(client)
