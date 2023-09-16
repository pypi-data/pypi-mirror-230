# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["Tests", "AsyncTests"]


class Tests(SyncAPIResource):
    def run_codegen(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Testing codegen change with new Github action"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/tests/run_codegen",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncTests(AsyncAPIResource):
    async def run_codegen(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Testing codegen change with new Github action"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/tests/run_codegen",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )
