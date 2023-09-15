# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from ...types.types import (
    ObjectMixedKnownAndUnknownResponse,
    ObjectMultiplePropertiesSameRefResponse,
    ObjectMultiplePropertiesSameModelResponse,
    ObjectMultipleArrayPropertiesSameRefResponse,
)
from ..._base_client import make_request_options

__all__ = ["Objects", "AsyncObjects"]


class Objects(SyncAPIResource):
    def mixed_known_and_unknown(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMixedKnownAndUnknownResponse:
        """
        Endpoint with a response schema object that contains a mix of known & unknown
        properties with the same value types.
        """
        return self._get(
            "/types/object/mixed_known_and_unknown",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMixedKnownAndUnknownResponse,
        )

    def multiple_array_properties_same_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultipleArrayPropertiesSameRefResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same $ref in array items that is _not_ a model in the config.
        Three child types should be generated, one for each property.
        """
        return self._get(
            "/types/object/multiple_array_properties_same_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultipleArrayPropertiesSameRefResponse,
        )

    def multiple_properties_same_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultiplePropertiesSameModelResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same model.
        """
        return self._get(
            "/types/object/multiple_properties_same_model",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultiplePropertiesSameModelResponse,
        )

    def multiple_properties_same_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultiplePropertiesSameRefResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same $ref that is _not_ a model in the config. Three child types
        should be generated. One for each property.
        """
        return self._get(
            "/types/object/multiple_properties_same_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultiplePropertiesSameRefResponse,
        )


class AsyncObjects(AsyncAPIResource):
    async def mixed_known_and_unknown(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMixedKnownAndUnknownResponse:
        """
        Endpoint with a response schema object that contains a mix of known & unknown
        properties with the same value types.
        """
        return await self._get(
            "/types/object/mixed_known_and_unknown",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMixedKnownAndUnknownResponse,
        )

    async def multiple_array_properties_same_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultipleArrayPropertiesSameRefResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same $ref in array items that is _not_ a model in the config.
        Three child types should be generated, one for each property.
        """
        return await self._get(
            "/types/object/multiple_array_properties_same_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultipleArrayPropertiesSameRefResponse,
        )

    async def multiple_properties_same_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultiplePropertiesSameModelResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same model.
        """
        return await self._get(
            "/types/object/multiple_properties_same_model",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultiplePropertiesSameModelResponse,
        )

    async def multiple_properties_same_ref(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMultiplePropertiesSameRefResponse:
        """
        Endpoint with a response schema object that contains multiple properties that
        reference the same $ref that is _not_ a model in the config. Three child types
        should be generated. One for each property.
        """
        return await self._get(
            "/types/object/multiple_properties_same_ref",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMultiplePropertiesSameRefResponse,
        )
