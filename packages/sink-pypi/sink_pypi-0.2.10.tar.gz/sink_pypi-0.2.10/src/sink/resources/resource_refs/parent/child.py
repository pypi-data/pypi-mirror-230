# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._base_client import make_request_options
from ....types.resource_refs.parent import ChildModel

__all__ = ["Child", "AsyncChild"]


class Child(SyncAPIResource):
    def returns_child_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ChildModel:
        """
        endpoint that returns a model that is referenced from a model in a parent
        resource
        """
        return self._get(
            "/resource_refs/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChildModel,
        )


class AsyncChild(AsyncAPIResource):
    async def returns_child_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ChildModel:
        """
        endpoint that returns a model that is referenced from a model in a parent
        resource
        """
        return await self._get(
            "/resource_refs/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChildModel,
        )
