# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._resource import SyncAPIResource, AsyncAPIResource
from ...pagination import SyncMyConcretePage, AsyncMyConcretePage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.pagination_tests import MyConcretePageItem, concrete_list_params

__all__ = ["Concrete", "AsyncConcrete"]


class Concrete(SyncAPIResource):
    def list(
        self,
        *,
        my_cursor: str,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> SyncMyConcretePage[MyConcretePageItem]:
        """
        Test case for concrete page types using cursor based pagination.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/concrete_cursor",
            page=SyncMyConcretePage[MyConcretePageItem],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "my_cursor": my_cursor,
                        "limit": limit,
                    },
                    concrete_list_params.ConcreteListParams,
                ),
            ),
            model=MyConcretePageItem,
        )


class AsyncConcrete(AsyncAPIResource):
    def list(
        self,
        *,
        my_cursor: str,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[MyConcretePageItem, AsyncMyConcretePage[MyConcretePageItem]]:
        """
        Test case for concrete page types using cursor based pagination.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/concrete_cursor",
            page=AsyncMyConcretePage[MyConcretePageItem],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "my_cursor": my_cursor,
                        "limit": limit,
                    },
                    concrete_list_params.ConcreteListParams,
                ),
            ),
            model=MyConcretePageItem,
        )
