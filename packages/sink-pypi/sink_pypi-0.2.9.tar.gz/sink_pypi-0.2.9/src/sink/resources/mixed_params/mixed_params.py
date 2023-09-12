# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...types import (
    mixed_param_query_and_body_params,
    mixed_param_query_body_and_path_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from .duplicates import Duplicates, AsyncDuplicates
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.shared import BasicSharedModelObject

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["MixedParams", "AsyncMixedParams"]


class MixedParams(SyncAPIResource):
    duplicates: Duplicates

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.duplicates = Duplicates(client)

    def query_and_body(
        self,
        *,
        query_param: str | NotGiven = NOT_GIVEN,
        body_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines both query and body params

        Args:
          query_param: Query param description

          body_param: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/mixed_params/query_and_body",
            body=maybe_transform(
                {"body_param": body_param}, mixed_param_query_and_body_params.MixedParamQueryAndBodyParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"query_param": query_param}, mixed_param_query_and_body_params.MixedParamQueryAndBodyParams
                ),
            ),
            cast_to=BasicSharedModelObject,
        )

    def query_body_and_path(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        query_param: str | NotGiven = NOT_GIVEN,
        body_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines query, body and path params

        Args:
          query_param: Query param description

          body_param: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            f"/mixed_params/query_body_and_path/{path_param}",
            body=maybe_transform(
                {"body_param": body_param}, mixed_param_query_body_and_path_params.MixedParamQueryBodyAndPathParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"query_param": query_param},
                    mixed_param_query_body_and_path_params.MixedParamQueryBodyAndPathParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )


class AsyncMixedParams(AsyncAPIResource):
    duplicates: AsyncDuplicates

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.duplicates = AsyncDuplicates(client)

    async def query_and_body(
        self,
        *,
        query_param: str | NotGiven = NOT_GIVEN,
        body_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines both query and body params

        Args:
          query_param: Query param description

          body_param: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/mixed_params/query_and_body",
            body=maybe_transform(
                {"body_param": body_param}, mixed_param_query_and_body_params.MixedParamQueryAndBodyParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"query_param": query_param}, mixed_param_query_and_body_params.MixedParamQueryAndBodyParams
                ),
            ),
            cast_to=BasicSharedModelObject,
        )

    async def query_body_and_path(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        query_param: str | NotGiven = NOT_GIVEN,
        body_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines query, body and path params

        Args:
          query_param: Query param description

          body_param: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            f"/mixed_params/query_body_and_path/{path_param}",
            body=maybe_transform(
                {"body_param": body_param}, mixed_param_query_body_and_path_params.MixedParamQueryBodyAndPathParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {"query_param": query_param},
                    mixed_param_query_body_and_path_params.MixedParamQueryBodyAndPathParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )
