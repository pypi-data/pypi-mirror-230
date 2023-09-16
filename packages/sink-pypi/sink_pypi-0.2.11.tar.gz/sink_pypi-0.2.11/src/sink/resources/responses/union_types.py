# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Any, cast

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.responses import (
    UnionTypeNumbersResponse,
    UnionTypeObjectsResponse,
    UnionTypeMixedTypesResponse,
)

__all__ = ["UnionTypes", "AsyncUnionTypes"]


class UnionTypes(SyncAPIResource):
    def mixed_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeMixedTypesResponse:
        """Endpoint with a top level union response of different types."""
        return cast(
            UnionTypeMixedTypesResponse,
            self._post(
                "/responses/unions/mixed_types",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeMixedTypesResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def numbers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeNumbersResponse:
        """Endpoint with a top level union response of floats and integers."""
        return cast(
            UnionTypeNumbersResponse,
            self._post(
                "/responses/unions/numbers",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeNumbersResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def objects(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeObjectsResponse:
        """Endpoint with a top level union response of just object variants."""
        return cast(
            UnionTypeObjectsResponse,
            self._post(
                "/responses/unions/objects",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeObjectsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncUnionTypes(AsyncAPIResource):
    async def mixed_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeMixedTypesResponse:
        """Endpoint with a top level union response of different types."""
        return cast(
            UnionTypeMixedTypesResponse,
            await self._post(
                "/responses/unions/mixed_types",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeMixedTypesResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def numbers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeNumbersResponse:
        """Endpoint with a top level union response of floats and integers."""
        return cast(
            UnionTypeNumbersResponse,
            await self._post(
                "/responses/unions/numbers",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeNumbersResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def objects(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> UnionTypeObjectsResponse:
        """Endpoint with a top level union response of just object variants."""
        return cast(
            UnionTypeObjectsResponse,
            await self._post(
                "/responses/unions/objects",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    idempotency_key=idempotency_key,
                ),
                cast_to=cast(
                    Any, UnionTypeObjectsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )
