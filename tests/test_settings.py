"""Tests for the Free Mobile SMS client settings."""

from __future__ import annotations

import os
from pathlib import Path

from freemobile_sms.settings import FreeMobileSettings


class TestFreeMobileSettings:
    """Tests for FreeMobileSettings pydantic model."""

    def test_default_values(self) -> None:
        """Settings should have sensible defaults."""
        s = FreeMobileSettings()
        assert s.api_url == "https://smsapi.free-mobile.fr/sendmsg"
        assert s.user == ""
        assert s.password == ""

    def test_explicit_values(self) -> None:
        """Settings should accept explicit values."""
        s = FreeMobileSettings(user="u", password="p", api_url="http://test")
        assert s.user == "u"
        assert s.password == "p"
        assert s.api_url == "http://test"

    def test_env_prefix(self) -> None:
        """Settings should load from FREE_MOBILE_ env prefix."""
        env = {
            "FREE_MOBILE_USER": "envuser",
            "FREE_MOBILE_PASSWORD": "envpass",
            "FREE_MOBILE_API_URL": "http://envtest",
        }
        original = {}
        for key, value in env.items():
            original[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            s = FreeMobileSettings()
            assert s.user == "envuser"
            assert s.password == "envpass"
            assert s.api_url == "http://envtest"
        finally:
            for key, orig_val in original.items():
                if orig_val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig_val

    def test_dotenv_file(self, tmp_path: Path) -> None:
        """Settings should load from a .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("FREE_MOBILE_USER=dotuser\nFREE_MOBILE_PASSWORD=dotpass\n")

        s = FreeMobileSettings(_env_file=str(env_file))
        assert s.user == "dotuser"
        assert s.password == "dotpass"

    def test_explicit_overrides_env(self) -> None:
        """Explicit values should override environment variables."""
        env = {
            "FREE_MOBILE_USER": "envuser",
        }
        original = {}
        for key, value in env.items():
            original[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            s = FreeMobileSettings(user="explicit_user")
            assert s.user == "explicit_user"
        finally:
            for key, orig_val in original.items():
                if orig_val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = orig_val
