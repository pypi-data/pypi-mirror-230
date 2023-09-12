# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .child import Child, AsyncChild
from ..._resource import SyncAPIResource, AsyncAPIResource

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Parent", "AsyncParent"]


class Parent(SyncAPIResource):
    child: Child

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.child = Child(client)


class AsyncParent(AsyncAPIResource):
    child: AsyncChild

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.child = AsyncChild(client)
