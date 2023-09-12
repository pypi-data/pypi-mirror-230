# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..types import (
    Address,
    EnvelopeWrappedArrayResponse,
    EnvelopeInlineResponseResponse,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._resource import SyncAPIResource, AsyncAPIResource
from .._wrappers import DataWrapper, ItemsWrapper
from .._base_client import make_request_options

__all__ = ["Envelopes", "AsyncEnvelopes"]


class Envelopes(SyncAPIResource):
    def explicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> Address:
        """Endpoint with a response wrapped within a `data` property."""
        response = self._get(
            "/envelopes/data",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DataWrapper[Address],
        )
        return response.data

    def implicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> Address:
        """Endpoint with a response wrapped within a `items` property."""
        response = self._get(
            "/envelopes/items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[Address],
        )
        return response.items

    def inline_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> EnvelopeInlineResponseResponse:
        """
        Endpoint with a response wrapped within a `items` property that doesn't use a
        $ref.
        """
        response = self._get(
            "/envelopes/items/inline_response",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[EnvelopeInlineResponseResponse],
        )
        return response.items

    def wrapped_array(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> EnvelopeWrappedArrayResponse:
        """
        Endpoint with a response wrapped within a `items` property that is an array
        type.
        """
        response = self._get(
            "/envelopes/items/wrapped_array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[EnvelopeWrappedArrayResponse],
        )
        return response.items


class AsyncEnvelopes(AsyncAPIResource):
    async def explicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> Address:
        """Endpoint with a response wrapped within a `data` property."""
        response = await self._get(
            "/envelopes/data",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DataWrapper[Address],
        )
        return response.data

    async def implicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> Address:
        """Endpoint with a response wrapped within a `items` property."""
        response = await self._get(
            "/envelopes/items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[Address],
        )
        return response.items

    async def inline_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> EnvelopeInlineResponseResponse:
        """
        Endpoint with a response wrapped within a `items` property that doesn't use a
        $ref.
        """
        response = await self._get(
            "/envelopes/items/inline_response",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[EnvelopeInlineResponseResponse],
        )
        return response.items

    async def wrapped_array(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> EnvelopeWrappedArrayResponse:
        """
        Endpoint with a response wrapped within a `items` property that is an array
        type.
        """
        response = await self._get(
            "/envelopes/items/wrapped_array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ItemsWrapper[EnvelopeWrappedArrayResponse],
        )
        return response.items
