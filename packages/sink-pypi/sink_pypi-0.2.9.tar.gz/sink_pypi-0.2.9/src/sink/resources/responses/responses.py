# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...types import (
    ObjectWithAnyOfNullProperty,
    ObjectWithOneOfNullProperty,
    ResponseAllofSimpleResponse,
    ResponseNestedArrayResponse,
    ResponseArrayResponseResponse,
    ResponseMissingRequiredResponse,
    ResponseAllofCrossResourceResponse,
    ResponseObjectNoPropertiesResponse,
    ResponseObjectAllPropertiesResponse,
    ResponseAdditionalPropertiesResponse,
    ResponseObjectWithAdditionalPropertiesPropResponse,
    ResponseAdditionalPropertiesNestedModelReferenceResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._resource import SyncAPIResource, AsyncAPIResource
from .union_types import UnionTypes, AsyncUnionTypes
from ..._base_client import make_request_options
from ...types.shared import SimpleObject

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Responses", "AsyncResponses"]


class Responses(SyncAPIResource):
    union_types: UnionTypes

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.union_types = UnionTypes(client)

    def additional_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseAdditionalPropertiesResponse:
        """Endpoint with a top level additionalProperties response."""
        return self._post(
            "/responses/additional_properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseAdditionalPropertiesResponse,
        )

    def additional_properties_nested_model_reference(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseAdditionalPropertiesNestedModelReferenceResponse:
        """
        Endpoint with a top level additionalProperties response where the items type
        points to an object defined as a model in the config.
        """
        return self._post(
            "/responses/additional_properties_nested_model_reference",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseAdditionalPropertiesNestedModelReferenceResponse,
        )

    def allof_cross_resource(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseAllofCrossResourceResponse:
        """
        Method with a response object defined using allOf and two models, one from
        another resource and one from this resource, as well as a nested allOf.
        """
        return self._get(
            "/responses/allof/cross",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseAllofCrossResourceResponse,
        )

    def allof_simple(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseAllofSimpleResponse:
        """
        Method with a response object defined using allOf and inline schema definitions.
        """
        return self._get(
            "/responses/allof/simple",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseAllofSimpleResponse,
        )

    def anyof_null(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectWithAnyOfNullProperty:
        """Method with a response object that uses anyOf to indicate nullability."""
        return self._get(
            "/responses/anyof_null",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectWithAnyOfNullProperty,
        )

    def array_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseArrayResponseResponse:
        """Endpoint that returns a top-level array."""
        return self._get(
            "/responses/array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseArrayResponseResponse,
        )

    def empty_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """Endpoint with an empty response."""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/responses/empty",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def missing_required(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseMissingRequiredResponse:
        """Endpoint with a response schema that doesn't set the `required` property."""
        return self._get(
            "/responses/missing_required",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseMissingRequiredResponse,
        )

    def nested_array(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseNestedArrayResponse:
        """Endpoint that returns a nested array."""
        return self._get(
            "/responses/nested_array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseNestedArrayResponse,
        )

    def object_all_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseObjectAllPropertiesResponse:
        """
        Method with a response object with a different property for each supported type.
        """
        return self._get(
            "/responses/object/everything",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseObjectAllPropertiesResponse,
        )

    def object_no_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseObjectNoPropertiesResponse:
        """Endpoint with an empty response."""
        return self._post(
            "/responses/object_no_properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseObjectNoPropertiesResponse,
        )

    def object_with_additional_properties_prop(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseObjectWithAdditionalPropertiesPropResponse:
        """
        Endpoint with an object response that contains an `additionalProperties`
        property with a nested schema.
        """
        return self._post(
            "/responses/object_with_additional_properties_prop",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseObjectWithAdditionalPropertiesPropResponse,
        )

    def oneof_null(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectWithOneOfNullProperty:
        """Method with a response object that uses oneOf to indicate nullability."""
        return self._get(
            "/responses/oneof_null",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectWithOneOfNullProperty,
        )

    def shared_response_object(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> SimpleObject:
        """Endpoint that returns a $ref to SimpleObject.

        This is used to test shared
        response models.
        """
        return self._get(
            "/responses/simple_object",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SimpleObject,
        )

    def string_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> str:
        """Endpoint with a top level string response."""
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return self._post(
            "/responses/string",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=str,
        )


class AsyncResponses(AsyncAPIResource):
    union_types: AsyncUnionTypes

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.union_types = AsyncUnionTypes(client)

    async def additional_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseAdditionalPropertiesResponse:
        """Endpoint with a top level additionalProperties response."""
        return await self._post(
            "/responses/additional_properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseAdditionalPropertiesResponse,
        )

    async def additional_properties_nested_model_reference(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseAdditionalPropertiesNestedModelReferenceResponse:
        """
        Endpoint with a top level additionalProperties response where the items type
        points to an object defined as a model in the config.
        """
        return await self._post(
            "/responses/additional_properties_nested_model_reference",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseAdditionalPropertiesNestedModelReferenceResponse,
        )

    async def allof_cross_resource(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseAllofCrossResourceResponse:
        """
        Method with a response object defined using allOf and two models, one from
        another resource and one from this resource, as well as a nested allOf.
        """
        return await self._get(
            "/responses/allof/cross",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseAllofCrossResourceResponse,
        )

    async def allof_simple(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseAllofSimpleResponse:
        """
        Method with a response object defined using allOf and inline schema definitions.
        """
        return await self._get(
            "/responses/allof/simple",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseAllofSimpleResponse,
        )

    async def anyof_null(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectWithAnyOfNullProperty:
        """Method with a response object that uses anyOf to indicate nullability."""
        return await self._get(
            "/responses/anyof_null",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectWithAnyOfNullProperty,
        )

    async def array_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseArrayResponseResponse:
        """Endpoint that returns a top-level array."""
        return await self._get(
            "/responses/array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseArrayResponseResponse,
        )

    async def empty_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """Endpoint with an empty response."""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/responses/empty",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def missing_required(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseMissingRequiredResponse:
        """Endpoint with a response schema that doesn't set the `required` property."""
        return await self._get(
            "/responses/missing_required",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseMissingRequiredResponse,
        )

    async def nested_array(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseNestedArrayResponse:
        """Endpoint that returns a nested array."""
        return await self._get(
            "/responses/nested_array",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseNestedArrayResponse,
        )

    async def object_all_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ResponseObjectAllPropertiesResponse:
        """
        Method with a response object with a different property for each supported type.
        """
        return await self._get(
            "/responses/object/everything",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ResponseObjectAllPropertiesResponse,
        )

    async def object_no_properties(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseObjectNoPropertiesResponse:
        """Endpoint with an empty response."""
        return await self._post(
            "/responses/object_no_properties",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseObjectNoPropertiesResponse,
        )

    async def object_with_additional_properties_prop(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ResponseObjectWithAdditionalPropertiesPropResponse:
        """
        Endpoint with an object response that contains an `additionalProperties`
        property with a nested schema.
        """
        return await self._post(
            "/responses/object_with_additional_properties_prop",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ResponseObjectWithAdditionalPropertiesPropResponse,
        )

    async def oneof_null(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ObjectWithOneOfNullProperty:
        """Method with a response object that uses oneOf to indicate nullability."""
        return await self._get(
            "/responses/oneof_null",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectWithOneOfNullProperty,
        )

    async def shared_response_object(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> SimpleObject:
        """Endpoint that returns a $ref to SimpleObject.

        This is used to test shared
        response models.
        """
        return await self._get(
            "/responses/simple_object",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SimpleObject,
        )

    async def string_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> str:
        """Endpoint with a top level string response."""
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return await self._post(
            "/responses/string",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=str,
        )
