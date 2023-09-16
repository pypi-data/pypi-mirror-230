# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .parent import Parent, AsyncParent
from ..._resource import SyncAPIResource, AsyncAPIResource
from .paginated_model_first_ref import (
    PaginatedModelFirstRef,
    AsyncPaginatedModelFirstRef,
)
from .paginated_model_second_ref import (
    PaginatedModelSecondRef,
    AsyncPaginatedModelSecondRef,
)

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["ResourceRefs", "AsyncResourceRefs"]


class ResourceRefs(SyncAPIResource):
    paginated_model_first_ref: PaginatedModelFirstRef
    paginated_model_second_ref: PaginatedModelSecondRef
    parent: Parent

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.paginated_model_first_ref = PaginatedModelFirstRef(client)
        self.paginated_model_second_ref = PaginatedModelSecondRef(client)
        self.parent = Parent(client)


class AsyncResourceRefs(AsyncAPIResource):
    paginated_model_first_ref: AsyncPaginatedModelFirstRef
    paginated_model_second_ref: AsyncPaginatedModelSecondRef
    parent: AsyncParent

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.paginated_model_first_ref = AsyncPaginatedModelFirstRef(client)
        self.paginated_model_second_ref = AsyncPaginatedModelSecondRef(client)
        self.parent = AsyncParent(client)
