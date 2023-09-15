# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING, Union
from datetime import date

from .params import Params, AsyncParams
from ...types import (
    NameChildPropImportClashResponse,
    NameResponseShadowsPydanticResponse,
    NamePropertiesCommonConflictsResponse,
    NameResponsePropertyClashesModelImportResponse,
    name_properties_common_conflicts_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from .renaming import Renaming, AsyncRenaming
from .documents import Documents, AsyncDocuments
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from ...types.shared import BasicSharedModelObject
from .reserved_names import ReservedNames, AsyncReservedNames

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["Names", "AsyncNames"]


class Names(SyncAPIResource):
    renaming: Renaming
    documents: Documents
    reserved_names: ReservedNames
    params: Params

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.renaming = Renaming(client)
        self.documents = Documents(client)
        self.reserved_names = ReservedNames(client)
        self.params = Params(client)

    def child_prop_import_clash(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> NameChildPropImportClashResponse:
        """
        Endpoint with request & response properties that could cause clashes due to
        imports.
        """
        return self._post(
            "/names/child_prop_import_clash",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NameChildPropImportClashResponse,
        )

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> BasicSharedModelObject:
        """Endpoint with the name `get` in the config."""
        return self._get(
            "/names/method_name_get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BasicSharedModelObject,
        )

    def properties_common_conflicts(
        self,
        *,
        bool: bool,
        bool_2: bool,
        date: Union[str, date],
        date_2: Union[str, date],
        float: float,
        float_2: float,
        int: int,
        int_2: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> NamePropertiesCommonConflictsResponse:
        """
        Endpoint with request & response properties that are likely to cause name
        conflicts.

        Args:
          bool_2: In certain languages the type declaration for this prop can shadow the `bool`
              property declaration.

          date: This shadows the stdlib `datetime.date` type in Python & causes type errors.

          date_2: In certain languages the type declaration for this prop can shadow the `date`
              property declaration.

          float_2: In certain languages the type declaration for this prop can shadow the `float`
              property declaration.

          int_2: In certain languages the type declaration for this prop can shadow the `int`
              property declaration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/names/properties_common_conflicts",
            body=maybe_transform(
                {
                    "bool": bool,
                    "bool_2": bool_2,
                    "date": date,
                    "date_2": date_2,
                    "float": float,
                    "float_2": float_2,
                    "int": int,
                    "int_2": int_2,
                },
                name_properties_common_conflicts_params.NamePropertiesCommonConflictsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NamePropertiesCommonConflictsResponse,
        )

    def response_property_clashes_model_import(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> NameResponsePropertyClashesModelImportResponse:
        """
        Endpoint with a response model property that can cause clashes with a model
        import.
        """
        return self._get(
            "/names/response_property_clashes_model_import",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NameResponsePropertyClashesModelImportResponse,
        )

    def response_shadows_pydantic(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> NameResponseShadowsPydanticResponse:
        """Endpoint with a response model property that would clash with pydantic."""
        return self._get(
            "/names/response_property_shadows_pydantic",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NameResponseShadowsPydanticResponse,
        )


class AsyncNames(AsyncAPIResource):
    renaming: AsyncRenaming
    documents: AsyncDocuments
    reserved_names: AsyncReservedNames
    params: AsyncParams

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.renaming = AsyncRenaming(client)
        self.documents = AsyncDocuments(client)
        self.reserved_names = AsyncReservedNames(client)
        self.params = AsyncParams(client)

    async def child_prop_import_clash(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> NameChildPropImportClashResponse:
        """
        Endpoint with request & response properties that could cause clashes due to
        imports.
        """
        return await self._post(
            "/names/child_prop_import_clash",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NameChildPropImportClashResponse,
        )

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> BasicSharedModelObject:
        """Endpoint with the name `get` in the config."""
        return await self._get(
            "/names/method_name_get",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BasicSharedModelObject,
        )

    async def properties_common_conflicts(
        self,
        *,
        bool: bool,
        bool_2: bool,
        date: Union[str, date],
        date_2: Union[str, date],
        float: float,
        float_2: float,
        int: int,
        int_2: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> NamePropertiesCommonConflictsResponse:
        """
        Endpoint with request & response properties that are likely to cause name
        conflicts.

        Args:
          bool_2: In certain languages the type declaration for this prop can shadow the `bool`
              property declaration.

          date: This shadows the stdlib `datetime.date` type in Python & causes type errors.

          date_2: In certain languages the type declaration for this prop can shadow the `date`
              property declaration.

          float_2: In certain languages the type declaration for this prop can shadow the `float`
              property declaration.

          int_2: In certain languages the type declaration for this prop can shadow the `int`
              property declaration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/names/properties_common_conflicts",
            body=maybe_transform(
                {
                    "bool": bool,
                    "bool_2": bool_2,
                    "date": date,
                    "date_2": date_2,
                    "float": float,
                    "float_2": float_2,
                    "int": int,
                    "int_2": int_2,
                },
                name_properties_common_conflicts_params.NamePropertiesCommonConflictsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NamePropertiesCommonConflictsResponse,
        )

    async def response_property_clashes_model_import(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> NameResponsePropertyClashesModelImportResponse:
        """
        Endpoint with a response model property that can cause clashes with a model
        import.
        """
        return await self._get(
            "/names/response_property_clashes_model_import",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NameResponsePropertyClashesModelImportResponse,
        )

    async def response_shadows_pydantic(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> NameResponseShadowsPydanticResponse:
        """Endpoint with a response model property that would clash with pydantic."""
        return await self._get(
            "/names/response_property_shadows_pydantic",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NameResponseShadowsPydanticResponse,
        )
