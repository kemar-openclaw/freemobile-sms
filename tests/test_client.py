"""Tests for the Free Mobile SMS client."""

from __future__ import annotations

from urllib.parse import unquote_plus

import httpx
import pytest

from freemobile_sms.client import (
    AccessDeniedError,
    AsyncFreeMobileClient,
    FreeMobileClient,
    FreeMobileClientError,
    RateLimitError,
    ServerError,
)
from freemobile_sms.settings import FreeMobileSettings


def _mock_transport(status_code: int) -> httpx.MockTransport:
    """Create a MockTransport that returns the given status code."""
    return httpx.MockTransport(lambda request: httpx.Response(status_code))


# ── Sync client ────────────────────────────────────────────────────────────


class TestFreeMobileClientInit:
    """Tests for FreeMobileClient initialization."""

    def test_default_settings(self) -> None:
        """Client should create default settings when none provided."""
        client = FreeMobileClient()
        assert client.settings.api_url == "https://smsapi.free-mobile.fr/sendmsg"
        client.close()

    def test_custom_settings(self, settings: FreeMobileSettings) -> None:
        """Client should use provided settings."""
        client = FreeMobileClient(settings=settings)
        assert client.settings.user == "12345678"
        client.close()

    def test_custom_http_client(self, settings: FreeMobileSettings) -> None:
        """Client should use provided httpx.Client."""
        http_client = httpx.Client()
        client = FreeMobileClient(settings=settings, http_client=http_client)
        client.close()
        http_client.close()

    def test_context_manager(self, settings: FreeMobileSettings) -> None:
        """Client should work as a context manager."""
        with FreeMobileClient(settings=settings) as client:
            assert client.settings.user == "12345678"

    def test_repr(self, settings: FreeMobileSettings) -> None:
        """repr should include user and api_url."""
        client = FreeMobileClient(settings=settings)
        r = repr(client)
        assert "12345678" in r
        assert "smsapi" in r
        client.close()


class TestFreeMobileClientSend:
    """Tests for FreeMobileClient.send()."""

    def test_send_success(self, test_settings: FreeMobileSettings) -> None:
        """Successful send should return SMSResult with ok=True."""
        transport = _mock_transport(200)
        http_client = httpx.Client(transport=transport)
        with FreeMobileClient(settings=test_settings, http_client=http_client) as client:
            result = client.send("Hello!")
        assert result.ok is True
        assert result.status_code == 200

    def test_send_post_method(self, test_settings: FreeMobileSettings) -> None:
        """POST method should send data in request body."""
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            # Parse request body (URL-decode values as httpx encodes them)
            body = request.content.decode("utf-8")
            for part in body.split("&"):
                key, value = part.split("=", 1)
                captured[key] = unquote_plus(value)
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        with FreeMobileClient(settings=test_settings, http_client=http_client) as client:
            client.send("Hello World", method="POST")

        assert captured["method"] == "POST"
        assert captured["user"] == "12345678"
        assert captured["pass"] == "testApiKey"
        assert captured["msg"] == "Hello World"

    def test_send_missing_parameter(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 400 should return SMSResult with ok=False."""
        transport = _mock_transport(400)
        http_client = httpx.Client(transport=transport)
        with FreeMobileClient(settings=test_settings, http_client=http_client) as client:
            result = client.send("test")
        assert result.ok is False
        assert result.status_code == 400

    def test_send_rate_limited(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 402 should raise RateLimitError."""
        transport = _mock_transport(402)
        http_client = httpx.Client(transport=transport)
        with (
            FreeMobileClient(settings=test_settings, http_client=http_client) as client,
            pytest.raises(RateLimitError, match="Too many SMS"),
        ):
            client.send("test")

    def test_send_access_denied(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 403 should raise AccessDeniedError."""
        transport = _mock_transport(403)
        http_client = httpx.Client(transport=transport)
        with (
            FreeMobileClient(settings=test_settings, http_client=http_client) as client,
            pytest.raises(AccessDeniedError, match="Service not activated"),
        ):
            client.send("test")

    def test_send_server_error(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 500 should raise ServerError."""
        transport = _mock_transport(500)
        http_client = httpx.Client(transport=transport)
        with (
            FreeMobileClient(settings=test_settings, http_client=http_client) as client,
            pytest.raises(ServerError, match="server error"),
        ):
            client.send("test")

    def test_send_missing_credentials(self) -> None:
        """Missing user/password should raise FreeMobileClientError."""
        settings = FreeMobileSettings(user="", password="")
        with (
            FreeMobileClient(settings=settings) as client,
            pytest.raises(FreeMobileClientError, match="Missing credentials"),
        ):
            client.send("test")

    def test_send_missing_user_only(self) -> None:
        """Missing user (with password) should raise FreeMobileClientError."""
        settings = FreeMobileSettings(user="", password="haspass")
        with (
            FreeMobileClient(settings=settings) as client,
            pytest.raises(FreeMobileClientError, match="Missing credentials"),
        ):
            client.send("test")

    def test_send_missing_password_only(self) -> None:
        """Missing password (with user) should raise FreeMobileClientError."""
        settings = FreeMobileSettings(user="hasuser", password="")
        with (
            FreeMobileClient(settings=settings) as client,
            pytest.raises(FreeMobileClientError, match="Missing credentials"),
        ):
            client.send("test")

    def test_send_unknown_status_code(self, test_settings: FreeMobileSettings) -> None:
        """An unexpected status code should return SMSResult with ok=False."""
        transport = _mock_transport(418)
        http_client = httpx.Client(transport=transport)
        with FreeMobileClient(settings=test_settings, http_client=http_client) as client:
            result = client.send("test")
        assert result.ok is False
        assert result.status_code == 418
        assert "Unknown status code" in result.message

    def test_send_includes_params_in_request(self, test_settings: FreeMobileSettings) -> None:
        """Request should include user, pass, and msg as query params."""
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured.update(dict(request.url.params))
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        with FreeMobileClient(settings=test_settings, http_client=http_client) as client:
            client.send("Hello World")

        assert captured["user"] == "12345678"
        assert captured["pass"] == "testApiKey"
        assert captured["msg"] == "Hello World"


# ── Async client ───────────────────────────────────────────────────────────


class TestAsyncFreeMobileClientInit:
    """Tests for AsyncFreeMobileClient initialization."""

    @pytest.mark.asyncio
    async def test_default_settings(self) -> None:
        """Async client should create default settings when none provided."""
        async with AsyncFreeMobileClient() as client:
            assert client.settings.api_url == "https://smsapi.free-mobile.fr/sendmsg"

    @pytest.mark.asyncio
    async def test_custom_settings(self, settings: FreeMobileSettings) -> None:
        """Async client should use provided settings."""
        async with AsyncFreeMobileClient(settings=settings) as client:
            assert client.settings.user == "12345678"

    @pytest.mark.asyncio
    async def test_custom_http_client(self, settings: FreeMobileSettings) -> None:
        """Async client should accept a custom httpx.AsyncClient."""
        http_client = httpx.AsyncClient()
        client = AsyncFreeMobileClient(settings=settings, http_client=http_client)
        await client.close()
        await http_client.aclose()

    @pytest.mark.asyncio
    async def test_repr(self, settings: FreeMobileSettings) -> None:
        """repr should include user and api_url."""
        async with AsyncFreeMobileClient(settings=settings) as client:
            r = repr(client)
        assert "12345678" in r
        assert "smsapi" in r


class TestAsyncFreeMobileClientSend:
    """Tests for AsyncFreeMobileClient.send()."""

    @pytest.mark.asyncio
    async def test_send_success(self, test_settings: FreeMobileSettings) -> None:
        """Successful async send should return SMSResult with ok=True."""
        transport = _mock_transport(200)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            result = await client.send("Hello!")
        assert result.ok is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_send_post_method(self, test_settings: FreeMobileSettings) -> None:
        """POST method should send data in request body."""
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            body = request.content.decode("utf-8")
            for part in body.split("&"):
                key, value = part.split("=", 1)
                captured[key] = unquote_plus(value)
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            await client.send("Hello World", method="POST")

        assert captured["method"] == "POST"
        assert captured["user"] == "12345678"
        assert captured["pass"] == "testApiKey"
        assert captured["msg"] == "Hello World"

    @pytest.mark.asyncio
    async def test_send_rate_limited(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 402 should raise RateLimitError in async client."""
        transport = _mock_transport(402)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            with pytest.raises(RateLimitError, match="Too many SMS"):
                await client.send("test")

    @pytest.mark.asyncio
    async def test_send_access_denied(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 403 should raise AccessDeniedError in async client."""
        transport = _mock_transport(403)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            with pytest.raises(AccessDeniedError, match="Service not activated"):
                await client.send("test")

    @pytest.mark.asyncio
    async def test_send_server_error(self, test_settings: FreeMobileSettings) -> None:
        """HTTP 500 should raise ServerError in async client."""
        transport = _mock_transport(500)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            with pytest.raises(ServerError, match="server error"):
                await client.send("test")

    @pytest.mark.asyncio
    async def test_send_missing_credentials(self) -> None:
        """Missing credentials should raise FreeMobileClientError in async client."""
        settings = FreeMobileSettings(user="", password="")
        async with AsyncFreeMobileClient(settings=settings) as client:
            with pytest.raises(FreeMobileClientError, match="Missing credentials"):
                await client.send("test")

    @pytest.mark.asyncio
    async def test_send_unknown_status_code(self, test_settings: FreeMobileSettings) -> None:
        """Unexpected status code should return SMSResult with ok=False."""
        transport = _mock_transport(418)
        http_client = httpx.AsyncClient(transport=transport)
        async with AsyncFreeMobileClient(settings=test_settings, http_client=http_client) as client:
            result = await client.send("test")
        assert result.ok is False
        assert "Unknown status code" in result.message
