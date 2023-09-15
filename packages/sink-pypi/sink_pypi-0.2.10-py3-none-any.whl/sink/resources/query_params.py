# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal

from ..types import (
    query_param_enum_params,
    query_param_array_params,
    query_param_all_of_params,
    query_param_any_of_params,
    query_param_object_params,
    query_param_one_of_params,
    query_param_primitives_params,
    query_param_any_of_string_or_array_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import make_request_options

__all__ = ["QueryParams", "AsyncQueryParams"]


class QueryParams(SyncAPIResource):
    def all_of(
        self,
        *,
        foo_and_bar: query_param_all_of_params.FooAndBar | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with allOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/allOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"foo_and_bar": foo_and_bar}, query_param_all_of_params.QueryParamAllOfParams),
            ),
            cast_to=NoneType,
        )

    def any_of(
        self,
        *,
        string_or_integer: Union[str, int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with anyOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/anyOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"string_or_integer": string_or_integer}, query_param_any_of_params.QueryParamAnyOfParams
                ),
            ),
            cast_to=NoneType,
        )

    def any_of_string_or_array(
        self,
        *,
        ids: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with anyOf query param that's string or array of strings

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/anyOfStringOrArray",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ids": ids}, query_param_any_of_string_or_array_params.QueryParamAnyOfStringOrArrayParams
                ),
            ),
            cast_to=NoneType,
        )

    def array(
        self,
        *,
        integer_array_param: List[int] | NotGiven = NOT_GIVEN,
        string_array_param: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with array query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/array",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "integer_array_param": integer_array_param,
                        "string_array_param": string_array_param,
                    },
                    query_param_array_params.QueryParamArrayParams,
                ),
            ),
            cast_to=NoneType,
        )

    def enum(
        self,
        *,
        integer_enum_param: Literal[100, 200] | NotGiven = NOT_GIVEN,
        nullable_integer_enum_param: Optional[Literal[100, 200]] | NotGiven = NOT_GIVEN,
        nullable_number_enum_param: Optional[Literal[100, 200]] | NotGiven = NOT_GIVEN,
        nullable_string_enum_param: Optional[Literal["foo", "bar"]] | NotGiven = NOT_GIVEN,
        number_enum_param: Literal[100, 200] | NotGiven = NOT_GIVEN,
        string_enum_param: Literal["foo", "bar"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with enum query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/enum",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "integer_enum_param": integer_enum_param,
                        "nullable_integer_enum_param": nullable_integer_enum_param,
                        "nullable_number_enum_param": nullable_number_enum_param,
                        "nullable_string_enum_param": nullable_string_enum_param,
                        "number_enum_param": number_enum_param,
                        "string_enum_param": string_enum_param,
                    },
                    query_param_enum_params.QueryParamEnumParams,
                ),
            ),
            cast_to=NoneType,
        )

    def object(
        self,
        *,
        object_param: query_param_object_params.ObjectParam | NotGiven = NOT_GIVEN,
        object_ref_param: query_param_object_params.ObjectRefParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with object query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/object",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "object_param": object_param,
                        "object_ref_param": object_ref_param,
                    },
                    query_param_object_params.QueryParamObjectParams,
                ),
            ),
            cast_to=NoneType,
        )

    def one_of(
        self,
        *,
        string_or_integer: Union[str, int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with oneOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/oneOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"string_or_integer": string_or_integer}, query_param_one_of_params.QueryParamOneOfParams
                ),
            ),
            cast_to=NoneType,
        )

    def primitives(
        self,
        *,
        boolean_param: bool | NotGiven = NOT_GIVEN,
        integer_param: int | NotGiven = NOT_GIVEN,
        number_param: float | NotGiven = NOT_GIVEN,
        string_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with a set of primitive type query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/query_params/primitives",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "boolean_param": boolean_param,
                        "integer_param": integer_param,
                        "number_param": number_param,
                        "string_param": string_param,
                    },
                    query_param_primitives_params.QueryParamPrimitivesParams,
                ),
            ),
            cast_to=NoneType,
        )


class AsyncQueryParams(AsyncAPIResource):
    async def all_of(
        self,
        *,
        foo_and_bar: query_param_all_of_params.FooAndBar | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with allOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/allOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"foo_and_bar": foo_and_bar}, query_param_all_of_params.QueryParamAllOfParams),
            ),
            cast_to=NoneType,
        )

    async def any_of(
        self,
        *,
        string_or_integer: Union[str, int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with anyOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/anyOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"string_or_integer": string_or_integer}, query_param_any_of_params.QueryParamAnyOfParams
                ),
            ),
            cast_to=NoneType,
        )

    async def any_of_string_or_array(
        self,
        *,
        ids: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with anyOf query param that's string or array of strings

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/anyOfStringOrArray",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ids": ids}, query_param_any_of_string_or_array_params.QueryParamAnyOfStringOrArrayParams
                ),
            ),
            cast_to=NoneType,
        )

    async def array(
        self,
        *,
        integer_array_param: List[int] | NotGiven = NOT_GIVEN,
        string_array_param: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with array query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/array",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "integer_array_param": integer_array_param,
                        "string_array_param": string_array_param,
                    },
                    query_param_array_params.QueryParamArrayParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def enum(
        self,
        *,
        integer_enum_param: Literal[100, 200] | NotGiven = NOT_GIVEN,
        nullable_integer_enum_param: Optional[Literal[100, 200]] | NotGiven = NOT_GIVEN,
        nullable_number_enum_param: Optional[Literal[100, 200]] | NotGiven = NOT_GIVEN,
        nullable_string_enum_param: Optional[Literal["foo", "bar"]] | NotGiven = NOT_GIVEN,
        number_enum_param: Literal[100, 200] | NotGiven = NOT_GIVEN,
        string_enum_param: Literal["foo", "bar"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with enum query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/enum",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "integer_enum_param": integer_enum_param,
                        "nullable_integer_enum_param": nullable_integer_enum_param,
                        "nullable_number_enum_param": nullable_number_enum_param,
                        "nullable_string_enum_param": nullable_string_enum_param,
                        "number_enum_param": number_enum_param,
                        "string_enum_param": string_enum_param,
                    },
                    query_param_enum_params.QueryParamEnumParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def object(
        self,
        *,
        object_param: query_param_object_params.ObjectParam | NotGiven = NOT_GIVEN,
        object_ref_param: query_param_object_params.ObjectRefParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with object query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/object",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "object_param": object_param,
                        "object_ref_param": object_ref_param,
                    },
                    query_param_object_params.QueryParamObjectParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def one_of(
        self,
        *,
        string_or_integer: Union[str, int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with oneOf query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/oneOf",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"string_or_integer": string_or_integer}, query_param_one_of_params.QueryParamOneOfParams
                ),
            ),
            cast_to=NoneType,
        )

    async def primitives(
        self,
        *,
        boolean_param: bool | NotGiven = NOT_GIVEN,
        integer_param: int | NotGiven = NOT_GIVEN,
        number_param: float | NotGiven = NOT_GIVEN,
        string_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Endpoint with a set of primitive type query params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/query_params/primitives",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "boolean_param": boolean_param,
                        "integer_param": integer_param,
                        "number_param": number_param,
                        "string_param": string_param,
                    },
                    query_param_primitives_params.QueryParamPrimitivesParams,
                ),
            ),
            cast_to=NoneType,
        )
