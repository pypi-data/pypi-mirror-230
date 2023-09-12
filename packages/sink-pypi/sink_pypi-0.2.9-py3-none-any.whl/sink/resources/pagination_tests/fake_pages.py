# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._resource import SyncAPIResource, AsyncAPIResource
from ...pagination import SyncFakePage, AsyncFakePage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.shared import SimpleObject
from ...types.pagination_tests import fake_page_list_params

__all__ = ["FakePages", "AsyncFakePages"]


class FakePages(SyncAPIResource):
    def list(
        self,
        *,
        my_fake_page_param: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> SyncFakePage[SimpleObject]:
        """
        Endpoint that returns a top-level array that is transformed into a fake_page.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/fake_page",
            page=SyncFakePage[SimpleObject],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"my_fake_page_param": my_fake_page_param}, fake_page_list_params.FakePageListParams
                ),
            ),
            model=SimpleObject,
        )


class AsyncFakePages(AsyncAPIResource):
    def list(
        self,
        *,
        my_fake_page_param: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[SimpleObject, AsyncFakePage[SimpleObject]]:
        """
        Endpoint that returns a top-level array that is transformed into a fake_page.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/fake_page",
            page=AsyncFakePage[SimpleObject],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"my_fake_page_param": my_fake_page_param}, fake_page_list_params.FakePageListParams
                ),
            ),
            model=SimpleObject,
        )
