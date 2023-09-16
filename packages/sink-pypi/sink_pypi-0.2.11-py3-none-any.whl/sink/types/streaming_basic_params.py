# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["StreamingBasicParamsBase", "BasicStreamingRequestNonStreaming", "BasicStreamingRequestStreaming"]


class StreamingBasicParamsBase(TypedDict, total=False):
    model: Required[str]

    prompt: Required[str]


class BasicStreamingRequestNonStreaming(StreamingBasicParamsBase):
    stream: Literal[False]


class BasicStreamingRequestStreaming(StreamingBasicParamsBase):
    stream: Required[Literal[True]]


StreamingBasicParams = Union[BasicStreamingRequestNonStreaming, BasicStreamingRequestStreaming]
