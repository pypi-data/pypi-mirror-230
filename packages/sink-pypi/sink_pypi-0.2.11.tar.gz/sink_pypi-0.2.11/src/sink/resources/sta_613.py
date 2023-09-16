# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import Sta613OnlyGlobalResponse, Sta613GlobalWithStandardResponse
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["Sta613", "AsyncSta613"]


class Sta613(SyncAPIResource):
    def global_with_standard(
        self,
        id: str,
        *,
        camel_cased_path: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Sta613GlobalWithStandardResponse:
        """
        The operation takes a path param that is able to be set at the client level
        alongside a standard path param.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if camel_cased_path is None:
            camel_cased_path = self._client._get_camel_case_path_param()

        return self._post(
            f"/sta_613/path_params/{camel_cased_path}/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Sta613GlobalWithStandardResponse,
        )

    def only_global(
        self,
        *,
        client_path_param: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Sta613OnlyGlobalResponse:
        """
        The operation takes a path param that is able to be set at the client level.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if client_path_param is None:
            client_path_param = self._client._get_client_path_param_param()

        return self._post(
            f"/sta_613/path_params/{client_path_param}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Sta613OnlyGlobalResponse,
        )


class AsyncSta613(AsyncAPIResource):
    async def global_with_standard(
        self,
        id: str,
        *,
        camel_cased_path: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Sta613GlobalWithStandardResponse:
        """
        The operation takes a path param that is able to be set at the client level
        alongside a standard path param.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if camel_cased_path is None:
            camel_cased_path = self._client._get_camel_case_path_param()

        return await self._post(
            f"/sta_613/path_params/{camel_cased_path}/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Sta613GlobalWithStandardResponse,
        )

    async def only_global(
        self,
        *,
        client_path_param: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Sta613OnlyGlobalResponse:
        """
        The operation takes a path param that is able to be set at the client level.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if client_path_param is None:
            client_path_param = self._client._get_client_path_param_param()

        return await self._post(
            f"/sta_613/path_params/{client_path_param}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Sta613OnlyGlobalResponse,
        )
