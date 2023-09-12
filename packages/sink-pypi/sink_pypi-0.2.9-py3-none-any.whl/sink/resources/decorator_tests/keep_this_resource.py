# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.decorator_tests import KeepThisResourceKeepThisMethodResponse

__all__ = ["KeepThisResource", "AsyncKeepThisResource"]


class KeepThisResource(SyncAPIResource):
    def keep_this_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> KeepThisResourceKeepThisMethodResponse:
        """
        Nested method that should render because it is not skipped nor are its
        ancestors.
        """
        return self._get(
            "/decorator_tests/nested/keep/this/method",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeepThisResourceKeepThisMethodResponse,
        )


class AsyncKeepThisResource(AsyncAPIResource):
    async def keep_this_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> KeepThisResourceKeepThisMethodResponse:
        """
        Nested method that should render because it is not skipped nor are its
        ancestors.
        """
        return await self._get(
            "/decorator_tests/nested/keep/this/method",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeepThisResourceKeepThisMethodResponse,
        )
