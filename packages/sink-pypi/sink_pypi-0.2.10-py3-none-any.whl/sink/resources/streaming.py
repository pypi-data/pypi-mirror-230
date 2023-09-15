# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import overload
from typing_extensions import Literal

from ..types import (
    StreamingBasicResponse,
    StreamingNestedParamsResponse,
    StreamingQueryParamDiscriminatorResponse,
    streaming_basic_params,
    streaming_nested_params_params,
    streaming_query_param_discriminator_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import required_args, maybe_transform
from .._resource import SyncAPIResource, AsyncAPIResource
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options

__all__ = ["Streaming", "AsyncStreaming"]


class Streaming(SyncAPIResource):
    @overload
    def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingBasicResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Stream[StreamingBasicResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingBasicResponse | Stream[StreamingBasicResponse]:
        return self._post(
            "/streaming/basic",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                },
                streaming_basic_params.StreamingBasicParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamingBasicResponse,
            stream=stream or False,
            stream_cls=Stream[StreamingBasicResponse],
        )

    @overload
    def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingNestedParamsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[True],
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Stream[StreamingNestedParamsResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingNestedParamsResponse | Stream[StreamingNestedParamsResponse]:
        return self._post(
            "/streaming/nested_params",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "parent_object": parent_object,
                    "stream": stream,
                },
                streaming_nested_params_params.StreamingNestedParamsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamingNestedParamsResponse,
            stream=stream or False,
            stream_cls=Stream[StreamingNestedParamsResponse],
        )

    @overload
    def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> StreamingQueryParamDiscriminatorResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> Stream[StreamingQueryParamDiscriminatorResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["prompt"], ["prompt", "should_stream"])
    def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> StreamingQueryParamDiscriminatorResponse | Stream[StreamingQueryParamDiscriminatorResponse]:
        return self._get(
            "/streaming/query_param_discriminator",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "prompt": prompt,
                        "should_stream": should_stream,
                    },
                    streaming_query_param_discriminator_params.StreamingQueryParamDiscriminatorParams,
                ),
            ),
            cast_to=StreamingQueryParamDiscriminatorResponse,
            stream=should_stream or False,
            stream_cls=Stream[StreamingQueryParamDiscriminatorResponse],
        )


class AsyncStreaming(AsyncAPIResource):
    @overload
    async def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingBasicResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    async def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> AsyncStream[StreamingBasicResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    async def basic(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingBasicResponse | AsyncStream[StreamingBasicResponse]:
        return await self._post(
            "/streaming/basic",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                },
                streaming_basic_params.StreamingBasicParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamingBasicResponse,
            stream=stream or False,
            stream_cls=AsyncStream[StreamingBasicResponse],
        )

    @overload
    async def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingNestedParamsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @overload
    async def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        stream: Literal[True],
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> AsyncStream[StreamingNestedParamsResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    async def nested_params(
        self,
        *,
        model: str,
        prompt: str,
        parent_object: streaming_nested_params_params.ParentObject | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> StreamingNestedParamsResponse | AsyncStream[StreamingNestedParamsResponse]:
        return await self._post(
            "/streaming/nested_params",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "parent_object": parent_object,
                    "stream": stream,
                },
                streaming_nested_params_params.StreamingNestedParamsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StreamingNestedParamsResponse,
            stream=stream or False,
            stream_cls=AsyncStream[StreamingNestedParamsResponse],
        )

    @overload
    async def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> StreamingQueryParamDiscriminatorResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[True],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[StreamingQueryParamDiscriminatorResponse]:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["prompt"], ["prompt", "should_stream"])
    async def query_param_discriminator(
        self,
        *,
        prompt: str,
        should_stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> StreamingQueryParamDiscriminatorResponse | AsyncStream[StreamingQueryParamDiscriminatorResponse]:
        return await self._get(
            "/streaming/query_param_discriminator",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "prompt": prompt,
                        "should_stream": should_stream,
                    },
                    streaming_query_param_discriminator_params.StreamingQueryParamDiscriminatorParams,
                ),
            ),
            cast_to=StreamingQueryParamDiscriminatorResponse,
            stream=should_stream or False,
            stream_cls=AsyncStream[StreamingQueryParamDiscriminatorResponse],
        )
