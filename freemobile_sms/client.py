"""Free Mobile SMS API client."""

from __future__ import annotations

from typing import Any

import httpx

from .models import FreeMobileStatus, SMSResult
from .settings import FreeMobileSettings


class FreeMobileClientError(Exception):
    """Base exception for Free Mobile client errors."""


class RateLimitError(FreeMobileClientError):
    """Raised when too many SMS have been sent in too short a time (HTTP 402)."""


class AccessDeniedError(FreeMobileClientError):
    """Raised when the service is not activated or credentials are wrong (HTTP 403)."""


class ServerError(FreeMobileClientError):
    """Raised when the Free Mobile server returns an internal error (HTTP 500)."""


# Map status codes to readable messages — matches the official Free Mobile docs.
_STATUS_MESSAGES: dict[int, str] = {
    FreeMobileStatus.OK: "SMS sent successfully",
    FreeMobileStatus.MISSING_PARAMETER: "Missing parameter — check user, pass, and msg",
    FreeMobileStatus.RATE_LIMITED: "Too many SMS sent in too short a time — slow down",
    FreeMobileStatus.ACCESS_DENIED: "Service not activated or incorrect login/key",
    FreeMobileStatus.SERVER_ERROR: "Free Mobile server error — try again later",
}


class FreeMobileClient:
    """Synchronous client for the Free Mobile SMS API.

    Args:
        settings: FreeMobileSettings instance. If not provided, loads from
            environment variables / .env file.
        http_client: Optional httpx.Client to use for requests. Useful for
            testing or custom configuration (proxies, timeouts, etc.).

    Examples:
        Send an SMS using environment variables::

            from freemobile_sms import FreeMobileClient

            client = FreeMobileClient()
            result = client.send("Hello from Python!")
            print(result.message)

        Send with explicit credentials::

            from freemobile_sms import FreeMobileClient, FreeMobileSettings

            settings = FreeMobileSettings(user="12345678", password="myApiKey")
            client = FreeMobileClient(settings=settings)
            result = client.send("Alert: server down!")
    """

    def __init__(
        self,
        settings: FreeMobileSettings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings or FreeMobileSettings()
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client()

    def _build_params(self, message: str) -> dict[str, str]:
        """Build query parameters for the API request."""
        return {
            "user": self.settings.user,
            "pass": self.settings.password,
            "msg": message,
        }

    def send(self, message: str, *, method: str = "GET") -> SMSResult:
        """Send an SMS notification.

        Args:
            message: The text message to send (max 480 characters).
            method: HTTP method — "GET" (default) or "POST".
                With POST the message doesn't need URL-encoding (per Free Mobile docs).

        Returns:
            SMSResult with success status, status code, and description.

        Raises:
            RateLimitError: When too many SMS have been sent in too short a time.
            AccessDeniedError: When the service is not activated or credentials are wrong.
            ServerError: When the Free Mobile server has an internal error.

        Examples:
            >>> client = FreeMobileClient(settings=settings)
            >>> result = client.send("Hello!")
            >>> result.ok
            True
        """
        if not self.settings.user or not self.settings.password:
            raise FreeMobileClientError(
                "Missing credentials — set FREE_MOBILE_USER and FREE_MOBILE_PASSWORD "
                "environment variables, or pass a FreeMobileSettings instance."
            )

        if method.upper() == "POST":
            response = self._client.post(
                self.settings.api_url,
                data={"user": self.settings.user, "pass": self.settings.password, "msg": message},
            )
        else:
            response = self._client.get(
                self.settings.api_url,
                params=self._build_params(message),
            )
        return self._handle_response(response.status_code)

    def _handle_response(self, status_code: int) -> SMSResult:
        """Convert an HTTP status code into an SMSResult, raising on errors."""
        msg = _STATUS_MESSAGES.get(status_code, f"Unknown status code: {status_code}")

        if status_code == FreeMobileStatus.RATE_LIMITED:
            raise RateLimitError(msg)
        if status_code == FreeMobileStatus.ACCESS_DENIED:
            raise AccessDeniedError(msg)
        if status_code == FreeMobileStatus.SERVER_ERROR:
            raise ServerError(msg)

        return SMSResult(
            success=status_code == FreeMobileStatus.OK,
            status_code=status_code,
            message=msg,
        )

    def close(self) -> None:
        """Close the underlying HTTP client if we own it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> FreeMobileClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"FreeMobileClient(user={self.settings.user!r}, api_url={self.settings.api_url!r})"


class AsyncFreeMobileClient:
    """Asynchronous client for the Free Mobile SMS API.

    Args:
        settings: FreeMobileSettings instance. If not provided, loads from
            environment variables / .env file.
        http_client: Optional httpx.AsyncClient for custom configuration.

    Examples:
        Send an SMS asynchronously::

            from freemobile_sms import AsyncFreeMobileClient

            async def notify():
                async with AsyncFreeMobileClient() as client:
                    result = await client.send("Hello async!")
                    print(result.message)
    """

    def __init__(
        self,
        settings: FreeMobileSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or FreeMobileSettings()
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient()

    def _build_params(self, message: str) -> dict[str, str]:
        """Build query parameters for the API request."""
        return {
            "user": self.settings.user,
            "pass": self.settings.password,
            "msg": message,
        }

    async def send(self, message: str, *, method: str = "GET") -> SMSResult:
        """Send an SMS notification asynchronously.

        Args:
            message: The text message to send.
            method: HTTP method — "GET" (default) or "POST".

        Returns:
            SMSResult with success status, status code, and description.

        Raises:
            RateLimitError: When too many SMS have been sent in too short a time.
            AccessDeniedError: When the service is not activated or credentials are wrong.
            ServerError: When the Free Mobile server has an internal error.
        """
        if not self.settings.user or not self.settings.password:
            raise FreeMobileClientError(
                "Missing credentials — set FREE_MOBILE_USER and FREE_MOBILE_PASSWORD "
                "environment variables, or pass a FreeMobileSettings instance."
            )

        if method.upper() == "POST":
            response = await self._client.post(
                self.settings.api_url,
                data={
                    "user": self.settings.user,
                    "pass": self.settings.password,
                    "msg": message,
                },
            )
        else:
            response = await self._client.get(
                self.settings.api_url,
                params=self._build_params(message),
            )
        return self._handle_response(response.status_code)

    def _handle_response(self, status_code: int) -> SMSResult:
        """Convert an HTTP status code into an SMSResult, raising on errors."""
        msg = _STATUS_MESSAGES.get(status_code, f"Unknown status code: {status_code}")

        if status_code == FreeMobileStatus.RATE_LIMITED:
            raise RateLimitError(msg)
        if status_code == FreeMobileStatus.ACCESS_DENIED:
            raise AccessDeniedError(msg)
        if status_code == FreeMobileStatus.SERVER_ERROR:
            raise ServerError(msg)

        return SMSResult(
            success=status_code == FreeMobileStatus.OK,
            status_code=status_code,
            message=msg,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncFreeMobileClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __repr__(self) -> str:
        return (
            f"AsyncFreeMobileClient(user={self.settings.user!r}, api_url={self.settings.api_url!r})"
        )
