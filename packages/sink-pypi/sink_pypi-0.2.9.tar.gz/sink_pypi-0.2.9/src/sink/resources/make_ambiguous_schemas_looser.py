# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import MakeAmbiguousSchemasLooserMakeAmbiguousSchemasLooserResponse
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["MakeAmbiguousSchemasLooser", "AsyncMakeAmbiguousSchemasLooser"]


class MakeAmbiguousSchemasLooser(SyncAPIResource):
    def make_ambiguous_schemas_looser(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> MakeAmbiguousSchemasLooserMakeAmbiguousSchemasLooserResponse:
        """Test case for makeAmbiguousSchemasLooser"""
        return self._get(
            "/make-ambiguous-schemas-looser",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MakeAmbiguousSchemasLooserMakeAmbiguousSchemasLooserResponse,
        )


class AsyncMakeAmbiguousSchemasLooser(AsyncAPIResource):
    async def make_ambiguous_schemas_looser(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> MakeAmbiguousSchemasLooserMakeAmbiguousSchemasLooserResponse:
        """Test case for makeAmbiguousSchemasLooser"""
        return await self._get(
            "/make-ambiguous-schemas-looser",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MakeAmbiguousSchemasLooserMakeAmbiguousSchemasLooserResponse,
        )
