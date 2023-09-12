# File generated from our OpenAPI spec by Stainless.

import re
from typing import Any, List, Type, Generic, Mapping, TypeVar, Optional, cast

from httpx import URL, Response

from ._types import ModelT
from ._utils import is_mapping
from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage
from .types.shared import SharedCursorNestedResponsePropMeta

__all__ = [
    "SyncCardPage",
    "AsyncCardPage",
    "SyncMyConcretePage",
    "AsyncMyConcretePage",
    "SyncPagePageNumber",
    "AsyncPagePageNumber",
    "SyncPageCursor",
    "AsyncPageCursor",
    "SyncPageCursorNestedResponseProp",
    "AsyncPageCursorNestedResponseProp",
    "SyncPageCursorURL",
    "AsyncPageCursorURL",
    "SyncPageOffset",
    "AsyncPageOffset",
    "SyncPageHypermedia",
    "AsyncPageHypermedia",
    "SyncPageHypermediaRaw",
    "AsyncPageHypermediaRaw",
    "SyncFakePage",
    "AsyncFakePage",
]

_BaseModelT = TypeVar("_BaseModelT", bound=BaseModel)

LINK_PATTERN = re.compile(r'<(?P<url>[^,]*)>; rel="(?P<rel>\w+)"')


class SyncCardPage(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    """Test description for card pages."""

    data: List[ModelT]
    page: int
    total_entries: int
    total_pages: int

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        current_page = self.page
        if not current_page < self.total_pages:
            return None
        return PageInfo(params={"page": current_page + 1})


class AsyncCardPage(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    """Test description for card pages."""

    data: List[ModelT]
    page: int
    total_entries: int
    total_pages: int

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        current_page = self.page
        if not current_page < self.total_pages:
            return None
        return PageInfo(params={"page": current_page + 1})


class SyncMyConcretePage(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    cursor: Optional[str]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.cursor
        if not cursor:
            return None

        return PageInfo(params={"my_cursor": cursor})


class AsyncMyConcretePage(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    cursor: Optional[str]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.cursor
        if not cursor:
            return None

        return PageInfo(params={"my_cursor": cursor})


class SyncPagePageNumber(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]
    last_page: int
    page: int

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        current_page = self.page
        if not current_page < self.last_page:
            return None
        return PageInfo(params={"page": current_page + 1})


class AsyncPagePageNumber(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]
    last_page: int
    page: int

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        current_page = self.page
        if not current_page < self.last_page:
            return None
        return PageInfo(params={"page": current_page + 1})


class SyncPageCursor(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    cursor: Optional[str]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.cursor
        if not cursor:
            return None

        return PageInfo(params={"cursor": cursor})


class AsyncPageCursor(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    cursor: Optional[str]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.cursor
        if not cursor:
            return None

        return PageInfo(params={"cursor": cursor})


class SyncPageCursorNestedResponseProp(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    meta: SharedCursorNestedResponsePropMeta
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.meta.pagination.cursor
        if not cursor:
            return None

        return PageInfo(params={"cursor": cursor})


class AsyncPageCursorNestedResponseProp(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    meta: SharedCursorNestedResponsePropMeta
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        cursor = self.meta.pagination.cursor
        if not cursor:
            return None

        return PageInfo(params={"cursor": cursor})


class SyncPageCursorURL(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    next_page: str
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        url = self.next_page
        if not url:
            return None

        return PageInfo(url=URL(url))


class AsyncPageCursorURL(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    next_page: str
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        url = self.next_page
        if not url:
            return None

        return PageInfo(url=URL(url))


class SyncPageOffset(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    count: int
    offset: int
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        offset = self.offset

        length = len(self.data)
        current_count = offset + length

        return PageInfo(params={"offset": current_count})


class AsyncPageOffset(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    count: int
    offset: int
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        offset = self.offset

        length = len(self.data)
        current_count = offset + length

        return PageInfo(params={"offset": current_count})


class PageHypermediaLinks(BaseModel):
    href: str

    rel: str


class SyncPageHypermedia(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    links: List[PageHypermediaLinks]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        try:
            next_link = next(filter(lambda l: l.rel == "next", self.links))
        except StopIteration:
            return None

        href = cast(Optional[str], next_link.href)
        if href is None:
            return None

        return PageInfo(url=URL(href))


class AsyncPageHypermedia(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    links: List[PageHypermediaLinks]
    data: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        try:
            next_link = next(filter(lambda l: l.rel == "next", self.links))
        except StopIteration:
            return None

        href = cast(Optional[str], next_link.href)
        if href is None:
            return None

        return PageInfo(url=URL(href))


class SyncPageHypermediaRaw(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]
    next_page_link: str

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        # TODO: store these links somewhere
        links = {match.group("rel"): match.group("url") for match in LINK_PATTERN.finditer(self.next_page_link)}
        next_url = links.get("next")
        if not next_url:
            return None

        return PageInfo(url=URL(next_url))

    @classmethod
    def build(cls: Type[_BaseModelT], *, response: Response, data: object) -> _BaseModelT:
        return cls.construct(
            **{
                **(cast(Mapping[str, Any], data) if is_mapping(data) else {}),
                "next_page_link": response.headers.get("NextPage"),
            }
        )


class AsyncPageHypermediaRaw(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    data: List[ModelT]
    next_page_link: str

    def _get_page_items(self) -> List[ModelT]:
        return self.data

    def next_page_info(self) -> Optional[PageInfo]:
        # TODO: store these links somewhere
        links = {match.group("rel"): match.group("url") for match in LINK_PATTERN.finditer(self.next_page_link)}
        next_url = links.get("next")
        if not next_url:
            return None

        return PageInfo(url=URL(next_url))

    @classmethod
    def build(cls: Type[_BaseModelT], *, response: Response, data: object) -> _BaseModelT:
        return cls.construct(
            **{
                **(cast(Mapping[str, Any], data) if is_mapping(data) else {}),
                "next_page_link": response.headers.get("NextPage"),
            }
        )


class SyncFakePage(BaseSyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    items: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.items

    def next_page_info(self) -> None:
        """
        This page represents a response that isn't actually paginated at the API level
        so there will never be a next page.
        """
        return None

    @classmethod
    def build(cls: Type[_BaseModelT], *, response: Response, data: object) -> _BaseModelT:
        return cls.construct(
            **{
                **(cast(Mapping[str, Any], data) if is_mapping(data) else {"items": data}),
            }
        )


class AsyncFakePage(BaseAsyncPage[ModelT], BasePage[ModelT], Generic[ModelT]):
    items: List[ModelT]

    def _get_page_items(self) -> List[ModelT]:
        return self.items

    def next_page_info(self) -> None:
        """
        This page represents a response that isn't actually paginated at the API level
        so there will never be a next page.
        """
        return None

    @classmethod
    def build(cls: Type[_BaseModelT], *, response: Response, data: object) -> _BaseModelT:
        return cls.construct(
            **{
                **(cast(Mapping[str, Any], data) if is_mapping(data) else {"items": data}),
            }
        )
