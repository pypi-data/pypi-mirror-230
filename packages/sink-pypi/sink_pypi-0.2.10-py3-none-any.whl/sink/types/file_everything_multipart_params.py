# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .._types import FileTypes

__all__ = ["FileEverythingMultipartParams"]


class FileEverythingMultipartParams(TypedDict, total=False):
    b: Required[bool]

    e: Required[Literal["a", "b", "c"]]

    file: Required[FileTypes]

    i: Required[int]

    n: Required[float]

    purpose: Required[str]

    s: Required[str]
