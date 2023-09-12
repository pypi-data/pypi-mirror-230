# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .cursor import Cursor, AsyncCursor
from .offset import Offset, AsyncOffset
from .concrete import Concrete, AsyncConcrete
from .cursor_url import CursorURL, AsyncCursorURL
from .fake_pages import FakePages, AsyncFakePages
from .hypermedia import Hypermedia, AsyncHypermedia
from ..._resource import SyncAPIResource, AsyncAPIResource
from .page_number import PageNumber, AsyncPageNumber
from .hypermedia_raw import HypermediaRaw, AsyncHypermediaRaw

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["PaginationTests", "AsyncPaginationTests"]


class PaginationTests(SyncAPIResource):
    concrete: Concrete
    page_number: PageNumber
    cursor: Cursor
    cursor_url: CursorURL
    offset: Offset
    fake_pages: FakePages
    hypermedia: Hypermedia
    hypermedia_raw: HypermediaRaw

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.concrete = Concrete(client)
        self.page_number = PageNumber(client)
        self.cursor = Cursor(client)
        self.cursor_url = CursorURL(client)
        self.offset = Offset(client)
        self.fake_pages = FakePages(client)
        self.hypermedia = Hypermedia(client)
        self.hypermedia_raw = HypermediaRaw(client)


class AsyncPaginationTests(AsyncAPIResource):
    concrete: AsyncConcrete
    page_number: AsyncPageNumber
    cursor: AsyncCursor
    cursor_url: AsyncCursorURL
    offset: AsyncOffset
    fake_pages: AsyncFakePages
    hypermedia: AsyncHypermedia
    hypermedia_raw: AsyncHypermediaRaw

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.concrete = AsyncConcrete(client)
        self.page_number = AsyncPageNumber(client)
        self.cursor = AsyncCursor(client)
        self.cursor_url = AsyncCursorURL(client)
        self.offset = AsyncOffset(client)
        self.fake_pages = AsyncFakePages(client)
        self.hypermedia = AsyncHypermedia(client)
        self.hypermedia_raw = AsyncHypermediaRaw(client)
