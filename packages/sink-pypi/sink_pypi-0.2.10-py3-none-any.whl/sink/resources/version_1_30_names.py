# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import Version1_30NameCreateResponse, version_1_30_name_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["Version1_30Names", "AsyncVersion1_30Names"]


class Version1_30Names(SyncAPIResource):
    def create(
        self,
        version_1_15: str | NotGiven = NOT_GIVEN,
        *,
        version_1_16: str | NotGiven = NOT_GIVEN,
        version_1_17: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Version1_30NameCreateResponse:
        """
        The `X-Client-Secret` header shouldn't be included in params definitions as it
        is already sent as a client argument.

        Whereas the `X-Custom-Endpoint-Header` should be included as it is only used
        here.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            f"/version_1_30_names/query/{version_1_15}",
            body=maybe_transform(
                {"version_1_17": version_1_17}, version_1_30_name_create_params.Version1_30NameCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"version_1_16": version_1_16}, version_1_30_name_create_params.Version1_30NameCreateParams
                ),
            ),
            cast_to=Version1_30NameCreateResponse,
        )


class AsyncVersion1_30Names(AsyncAPIResource):
    async def create(
        self,
        version_1_15: str | NotGiven = NOT_GIVEN,
        *,
        version_1_16: str | NotGiven = NOT_GIVEN,
        version_1_17: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Version1_30NameCreateResponse:
        """
        The `X-Client-Secret` header shouldn't be included in params definitions as it
        is already sent as a client argument.

        Whereas the `X-Custom-Endpoint-Header` should be included as it is only used
        here.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            f"/version_1_30_names/query/{version_1_15}",
            body=maybe_transform(
                {"version_1_17": version_1_17}, version_1_30_name_create_params.Version1_30NameCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"version_1_16": version_1_16}, version_1_30_name_create_params.Version1_30NameCreateParams
                ),
            ),
            cast_to=Version1_30NameCreateResponse,
        )
