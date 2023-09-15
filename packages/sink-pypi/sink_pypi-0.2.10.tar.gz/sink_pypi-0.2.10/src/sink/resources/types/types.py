# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .arrays import Arrays, AsyncArrays
from ...types import (
    TypeDatesResponse,
    TypeEnumsResponse,
    TypeDatetimesResponse,
    shared_params,
    type_dates_params,
    type_enums_params,
    type_datetimes_params,
    type_enum_tests_array_unique_values_params,
    type_enum_tests_array_unique_values_numbers_params,
    type_enum_tests_array_unique_values_2_values_params,
)
from .objects import Objects, AsyncObjects
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from .read_only_params import ReadOnlyParams, AsyncReadOnlyParams
from .write_only_responses import WriteOnlyResponses, AsyncWriteOnlyResponses

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Types", "AsyncTypes"]


class Types(SyncAPIResource):
    read_only_params: ReadOnlyParams
    write_only_responses: WriteOnlyResponses
    objects: Objects
    arrays: Arrays

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.read_only_params = ReadOnlyParams(client)
        self.write_only_responses = WriteOnlyResponses(client)
        self.objects = Objects(client)
        self.arrays = Arrays(client)

    def dates(
        self,
        *,
        required_date: Union[str, date],
        required_nullable_date: Union[str, date, None],
        list_date: List[Union[str, date]] | NotGiven = NOT_GIVEN,
        oneof_date: Union[Union[str, date], int] | NotGiven = NOT_GIVEN,
        optional_date: Union[str, date] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeDatesResponse:
        """
        Endpoint that has date types should generate params/responses with rich date
        types.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/types/dates",
            body=maybe_transform(
                {
                    "required_date": required_date,
                    "required_nullable_date": required_nullable_date,
                    "list_date": list_date,
                    "oneof_date": oneof_date,
                    "optional_date": optional_date,
                },
                type_dates_params.TypeDatesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeDatesResponse,
        )

    def datetimes(
        self,
        *,
        required_datetime: Union[str, datetime],
        required_nullable_datetime: Union[str, datetime, None],
        list_datetime: List[Union[str, datetime]] | NotGiven = NOT_GIVEN,
        oneof_datetime: Union[Union[str, datetime], int] | NotGiven = NOT_GIVEN,
        optional_datetime: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeDatetimesResponse:
        """
        Endpoint that has date-time types.

        Args:
          oneof_datetime: union type coming from the `oneof_datetime` property

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/types/datetimes",
            body=maybe_transform(
                {
                    "required_datetime": required_datetime,
                    "required_nullable_datetime": required_nullable_datetime,
                    "list_datetime": list_datetime,
                    "oneof_datetime": oneof_datetime,
                    "optional_datetime": optional_datetime,
                },
                type_datetimes_params.TypeDatetimesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeDatetimesResponse,
        )

    def enum_tests_array_unique_values(
        self,
        *,
        body: List[Literal["USD", "GBP", "PAB", "AED"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values",
            body=maybe_transform(body, type_enum_tests_array_unique_values_params.TypeEnumTestsArrayUniqueValuesParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def enum_tests_array_unique_values_2_values(
        self,
        *,
        body: List[Literal["USD", "GBP"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values_2_values",
            body=maybe_transform(
                body, type_enum_tests_array_unique_values_2_values_params.TypeEnumTestsArrayUniqueValues2ValuesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def enum_tests_array_unique_values_numbers(
        self,
        *,
        body: List[Literal[5, 6, 7, 8]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values_numbers",
            body=maybe_transform(
                body, type_enum_tests_array_unique_values_numbers_params.TypeEnumTestsArrayUniqueValuesNumbersParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def enums(
        self,
        *,
        input_currency: Optional[shared_params.Currency] | NotGiven = NOT_GIVEN,
        problematic_enum: Literal["123_FOO", "30%"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeEnumsResponse:
        """
        Endpoint that has a `$ref`d enum type in the request body and the response body.

        Args:
          input_currency: This is my description for the Currency enum

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/types/enums",
            body=maybe_transform(
                {
                    "input_currency": input_currency,
                    "problematic_enum": problematic_enum,
                },
                type_enums_params.TypeEnumsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeEnumsResponse,
        )


class AsyncTypes(AsyncAPIResource):
    read_only_params: AsyncReadOnlyParams
    write_only_responses: AsyncWriteOnlyResponses
    objects: AsyncObjects
    arrays: AsyncArrays

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.read_only_params = AsyncReadOnlyParams(client)
        self.write_only_responses = AsyncWriteOnlyResponses(client)
        self.objects = AsyncObjects(client)
        self.arrays = AsyncArrays(client)

    async def dates(
        self,
        *,
        required_date: Union[str, date],
        required_nullable_date: Union[str, date, None],
        list_date: List[Union[str, date]] | NotGiven = NOT_GIVEN,
        oneof_date: Union[Union[str, date], int] | NotGiven = NOT_GIVEN,
        optional_date: Union[str, date] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeDatesResponse:
        """
        Endpoint that has date types should generate params/responses with rich date
        types.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/types/dates",
            body=maybe_transform(
                {
                    "required_date": required_date,
                    "required_nullable_date": required_nullable_date,
                    "list_date": list_date,
                    "oneof_date": oneof_date,
                    "optional_date": optional_date,
                },
                type_dates_params.TypeDatesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeDatesResponse,
        )

    async def datetimes(
        self,
        *,
        required_datetime: Union[str, datetime],
        required_nullable_datetime: Union[str, datetime, None],
        list_datetime: List[Union[str, datetime]] | NotGiven = NOT_GIVEN,
        oneof_datetime: Union[Union[str, datetime], int] | NotGiven = NOT_GIVEN,
        optional_datetime: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeDatetimesResponse:
        """
        Endpoint that has date-time types.

        Args:
          oneof_datetime: union type coming from the `oneof_datetime` property

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/types/datetimes",
            body=maybe_transform(
                {
                    "required_datetime": required_datetime,
                    "required_nullable_datetime": required_nullable_datetime,
                    "list_datetime": list_datetime,
                    "oneof_datetime": oneof_datetime,
                    "optional_datetime": optional_datetime,
                },
                type_datetimes_params.TypeDatetimesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeDatetimesResponse,
        )

    async def enum_tests_array_unique_values(
        self,
        *,
        body: List[Literal["USD", "GBP", "PAB", "AED"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values",
            body=maybe_transform(body, type_enum_tests_array_unique_values_params.TypeEnumTestsArrayUniqueValuesParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def enum_tests_array_unique_values_2_values(
        self,
        *,
        body: List[Literal["USD", "GBP"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values_2_values",
            body=maybe_transform(
                body, type_enum_tests_array_unique_values_2_values_params.TypeEnumTestsArrayUniqueValues2ValuesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def enum_tests_array_unique_values_numbers(
        self,
        *,
        body: List[Literal[5, 6, 7, 8]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values_numbers",
            body=maybe_transform(
                body, type_enum_tests_array_unique_values_numbers_params.TypeEnumTestsArrayUniqueValuesNumbersParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def enums(
        self,
        *,
        input_currency: Optional[shared_params.Currency] | NotGiven = NOT_GIVEN,
        problematic_enum: Literal["123_FOO", "30%"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> TypeEnumsResponse:
        """
        Endpoint that has a `$ref`d enum type in the request body and the response body.

        Args:
          input_currency: This is my description for the Currency enum

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/types/enums",
            body=maybe_transform(
                {
                    "input_currency": input_currency,
                    "problematic_enum": problematic_enum,
                },
                type_enums_params.TypeEnumsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TypeEnumsResponse,
        )
