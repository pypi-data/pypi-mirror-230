# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "StreamingQueryParamDiscriminatorParamsBase",
    "QueryParamDiscriminatorRequestNonStreaming",
    "QueryParamDiscriminatorRequestStreaming",
]


class StreamingQueryParamDiscriminatorParamsBase(TypedDict, total=False):
    prompt: Required[str]


class QueryParamDiscriminatorRequestNonStreaming(StreamingQueryParamDiscriminatorParamsBase):
    should_stream: Literal[False]


class QueryParamDiscriminatorRequestStreaming(StreamingQueryParamDiscriminatorParamsBase):
    should_stream: Required[Literal[True]]


StreamingQueryParamDiscriminatorParams = Union[
    QueryParamDiscriminatorRequestNonStreaming, QueryParamDiscriminatorRequestStreaming
]
