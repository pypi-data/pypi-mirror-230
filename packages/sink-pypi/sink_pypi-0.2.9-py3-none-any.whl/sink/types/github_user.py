# File generated from our OpenAPI spec by Stainless.

from .._models import BaseModel
from .github_user_preferences import GithubUserPreferences

__all__ = ["GithubUser"]


class GithubUser(BaseModel):
    email: str
    """Someone's email address."""

    preferences: GithubUserPreferences
