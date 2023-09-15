# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.shared import BasicSharedModelObject
from ...types.mixed_params import (
    duplicate_body_and_path_params,
    duplicate_query_and_body_params,
    duplicate_query_and_path_params,
)

__all__ = ["Duplicates", "AsyncDuplicates"]


class Duplicates(SyncAPIResource):
    def body_and_path(
        self,
        path_id: str,
        body_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and body params

        Args:
          id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            f"/mixed_params/duplicates/body_and_path/{path_id}",
            body=maybe_transform({"id": body_id}, duplicate_body_and_path_params.DuplicateBodyAndPathParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BasicSharedModelObject,
        )

    def query_and_body(
        self,
        *,
        query_id: str,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in query
        and body params

        Args:
          id: Query param description

          id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/mixed_params/duplicates/query_and_body",
            body=maybe_transform({"id": body_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            ),
            cast_to=BasicSharedModelObject,
        )

    def query_and_path(
        self,
        path_id: str,
        query_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and query params

        Args:
          id: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            f"/mixed_params/duplicates/query_and_path/{path_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_path_params.DuplicateQueryAndPathParams),
            ),
            cast_to=BasicSharedModelObject,
        )


class AsyncDuplicates(AsyncAPIResource):
    async def body_and_path(
        self,
        path_id: str,
        body_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and body params

        Args:
          id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            f"/mixed_params/duplicates/body_and_path/{path_id}",
            body=maybe_transform({"id": body_id}, duplicate_body_and_path_params.DuplicateBodyAndPathParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BasicSharedModelObject,
        )

    async def query_and_body(
        self,
        *,
        query_id: str,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in query
        and body params

        Args:
          id: Query param description

          id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/mixed_params/duplicates/query_and_body",
            body=maybe_transform({"id": body_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            ),
            cast_to=BasicSharedModelObject,
        )

    async def query_and_path(
        self,
        path_id: str,
        query_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and query params

        Args:
          id: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            f"/mixed_params/duplicates/query_and_path/{path_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_path_params.DuplicateQueryAndPathParams),
            ),
            cast_to=BasicSharedModelObject,
        )
