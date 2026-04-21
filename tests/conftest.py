"""Test fixtures for the Free Mobile SMS client tests."""

from __future__ import annotations

import pytest

from freemobile_sms import FreeMobileSettings


@pytest.fixture
def settings() -> FreeMobileSettings:
    """Return a FreeMobileSettings with test credentials."""
    return FreeMobileSettings(
        user="12345678",
        password="testApiKey",
        api_url="https://smsapi.free-mobile.fr/sendmsg",
    )


@pytest.fixture
def mock_api_url() -> str:
    """Return a fake API URL for mocked requests."""
    return "https://smsapi.test.example.com/sendmsg"


@pytest.fixture
def test_settings(mock_api_url: str) -> FreeMobileSettings:
    """Return a FreeMobileSettings pointing to the mock API URL."""
    return FreeMobileSettings(
        user="12345678",
        password="testApiKey",
        api_url=mock_api_url,
    )
