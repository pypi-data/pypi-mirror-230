# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import shared_query_param_delete_params, shared_query_param_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["SharedQueryParams", "AsyncSharedQueryParams"]


class SharedQueryParams(SyncAPIResource):
    def retrieve(
        self,
        *,
        get1: str | NotGiven = NOT_GIVEN,
        shared1: str | NotGiven = NOT_GIVEN,
        shared2: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return self._get(
            "/shared-query-params",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "get1": get1,
                        "shared1": shared1,
                        "shared2": shared2,
                    },
                    shared_query_param_retrieve_params.SharedQueryParamRetrieveParams,
                ),
            ),
            cast_to=str,
        )

    def delete(
        self,
        *,
        get1: str | NotGiven = NOT_GIVEN,
        shared1: str | NotGiven = NOT_GIVEN,
        shared2: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return self._delete(
            "/shared-query-params",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {
                        "get1": get1,
                        "shared1": shared1,
                        "shared2": shared2,
                    },
                    shared_query_param_delete_params.SharedQueryParamDeleteParams,
                ),
            ),
            cast_to=str,
        )


class AsyncSharedQueryParams(AsyncAPIResource):
    async def retrieve(
        self,
        *,
        get1: str | NotGiven = NOT_GIVEN,
        shared1: str | NotGiven = NOT_GIVEN,
        shared2: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return await self._get(
            "/shared-query-params",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "get1": get1,
                        "shared1": shared1,
                        "shared2": shared2,
                    },
                    shared_query_param_retrieve_params.SharedQueryParamRetrieveParams,
                ),
            ),
            cast_to=str,
        )

    async def delete(
        self,
        *,
        get1: str | NotGiven = NOT_GIVEN,
        shared1: str | NotGiven = NOT_GIVEN,
        shared2: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return await self._delete(
            "/shared-query-params",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {
                        "get1": get1,
                        "shared1": shared1,
                        "shared2": shared2,
                    },
                    shared_query_param_delete_params.SharedQueryParamDeleteParams,
                ),
            ),
            cast_to=str,
        )
