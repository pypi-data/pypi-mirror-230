# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from ...types.names import RenamingExplicitResponsePropertyResponse
from ..._base_client import make_request_options

__all__ = ["Renaming", "AsyncRenaming"]


class Renaming(SyncAPIResource):
    def explicit_response_property(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> RenamingExplicitResponsePropertyResponse:
        """Endpoint with a renamed response property in each language."""
        return self._get(
            "/names/renaming/explicit_response_property",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RenamingExplicitResponsePropertyResponse,
        )


class AsyncRenaming(AsyncAPIResource):
    async def explicit_response_property(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> RenamingExplicitResponsePropertyResponse:
        """Endpoint with a renamed response property in each language."""
        return await self._get(
            "/names/renaming/explicit_response_property",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RenamingExplicitResponsePropertyResponse,
        )
