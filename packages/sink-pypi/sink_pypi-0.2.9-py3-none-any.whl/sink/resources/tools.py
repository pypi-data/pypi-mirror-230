# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import ObjectSkippedProps, tool_skipped_params_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["Tools", "AsyncTools"]


class Tools(SyncAPIResource):
    def skipped_params(
        self,
        *,
        skipped_go: str | NotGiven = NOT_GIVEN,
        skipped_java: str | NotGiven = NOT_GIVEN,
        skipped_node: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ObjectSkippedProps:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/tools/skipped_params",
            body=maybe_transform(
                {
                    "skipped_go": skipped_go,
                    "skipped_java": skipped_java,
                    "skipped_node": skipped_node,
                },
                tool_skipped_params_params.ToolSkippedParamsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ObjectSkippedProps,
        )


class AsyncTools(AsyncAPIResource):
    async def skipped_params(
        self,
        *,
        skipped_go: str | NotGiven = NOT_GIVEN,
        skipped_java: str | NotGiven = NOT_GIVEN,
        skipped_node: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ObjectSkippedProps:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/tools/skipped_params",
            body=maybe_transform(
                {
                    "skipped_go": skipped_go,
                    "skipped_java": skipped_java,
                    "skipped_node": skipped_node,
                },
                tool_skipped_params_params.ToolSkippedParamsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ObjectSkippedProps,
        )
