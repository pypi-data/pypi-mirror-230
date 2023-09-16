# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ...types import DecoratorTestKeepMeResponse
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .languages import Languages, AsyncLanguages
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._base_client import make_request_options
from .keep_this_resource import KeepThisResource, AsyncKeepThisResource

if TYPE_CHECKING:
    from ..._client import Sink, AsyncSink

__all__ = ["DecoratorTests", "AsyncDecoratorTests"]


class DecoratorTests(SyncAPIResource):
    languages: Languages
    keep_this_resource: KeepThisResource

    def __init__(self, client: Sink) -> None:
        super().__init__(client)
        self.languages = Languages(client)
        self.keep_this_resource = KeepThisResource(client)

    def keep_me(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> DecoratorTestKeepMeResponse:
        """Top-level method that should not be skipped."""
        return self._get(
            "/decorator_tests/keep/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecoratorTestKeepMeResponse,
        )


class AsyncDecoratorTests(AsyncAPIResource):
    languages: AsyncLanguages
    keep_this_resource: AsyncKeepThisResource

    def __init__(self, client: AsyncSink) -> None:
        super().__init__(client)
        self.languages = AsyncLanguages(client)
        self.keep_this_resource = AsyncKeepThisResource(client)

    async def keep_me(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> DecoratorTestKeepMeResponse:
        """Top-level method that should not be skipped."""
        return await self._get(
            "/decorator_tests/keep/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DecoratorTestKeepMeResponse,
        )
