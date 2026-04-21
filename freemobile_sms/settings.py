"""Pydantic Settings for Free Mobile SMS client configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class FreeMobileSettings(BaseSettings):
    """Configuration for the Free Mobile SMS API.

    Values are loaded from environment variables or a `.env` file.
    Prefix ``FREE_MOBILE_`` is prepended to environment variable names.

    Attributes:
        user: Your Free Mobile customer ID (login).
        password: Your Free Mobile API key (found in your account settings).
        api_url: The Free Mobile SMS API endpoint. Override for testing.
    """

    model_config = SettingsConfigDict(
        env_prefix="FREE_MOBILE_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    user: str = ""
    password: str = ""
    api_url: str = "https://smsapi.free-mobile.fr/sendmsg"
