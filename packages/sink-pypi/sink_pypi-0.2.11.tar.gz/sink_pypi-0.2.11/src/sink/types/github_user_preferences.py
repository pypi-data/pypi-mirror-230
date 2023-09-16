# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["GithubUserPreferences"]


class GithubUserPreferences(BaseModel):
    commit_email: str
    """What email they want in their commit messages"""

    commit_name: str
    """What name they want in their commit messages"""

    diff_style: Literal["interleaved", "side_by_side"]
    """Do they prefer view Git diffs side by side, or interleaved?"""
