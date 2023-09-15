# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from .child import Child, AsyncChild
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._base_client import make_request_options
from ....types.resource_refs import ParentModelWithChildRef

if TYPE_CHECKING:
    from ...._client import Sink, AsyncSink

__all__ = ["Parent", "AsyncParent"]


class Parent(SyncAPIResource):
    child: Child

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.child = Child(client)

    def returns_parent_model_with_child_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ParentModelWithChildRef:
        """endpoint that returns a model that has a nested reference to a child model"""
        return self._get(
            "/resource_refs/parent_with_child_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ParentModelWithChildRef,
        )


class AsyncParent(AsyncAPIResource):
    child: AsyncChild

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.child = AsyncChild(client)

    async def returns_parent_model_with_child_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ParentModelWithChildRef:
        """endpoint that returns a model that has a nested reference to a child model"""
        return await self._get(
            "/resource_refs/parent_with_child_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ParentModelWithChildRef,
        )
