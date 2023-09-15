# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.invalid_schemas import ObjectMissingItemsResponse

__all__ = ["Objects", "AsyncObjects"]


class Objects(SyncAPIResource):
    def missing_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMissingItemsResponse:
        return self._get(
            "/invalid_schemas/objects/property_missing_def",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMissingItemsResponse,
        )


class AsyncObjects(AsyncAPIResource):
    async def missing_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMissingItemsResponse:
        return await self._get(
            "/invalid_schemas/objects/property_missing_def",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMissingItemsResponse,
        )
