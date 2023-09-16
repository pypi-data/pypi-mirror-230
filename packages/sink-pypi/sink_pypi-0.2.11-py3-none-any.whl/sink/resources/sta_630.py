# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import GithubUser
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["Sta630", "AsyncSta630"]


class Sta630(SyncAPIResource):
    def nested_path(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> GithubUser:
        """
        Should return a GithubUser object with a `properties` field that we can rename
        in the Stainless config to a prettier name.
        """
        return self._get(
            "/sta_630/define_models_nested_path",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GithubUser,
        )


class AsyncSta630(AsyncAPIResource):
    async def nested_path(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> GithubUser:
        """
        Should return a GithubUser object with a `properties` field that we can rename
        in the Stainless config to a prettier name.
        """
        return await self._get(
            "/sta_630/define_models_nested_path",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GithubUser,
        )
