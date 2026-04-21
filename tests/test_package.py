"""Tests for package-level imports and __all__."""

from __future__ import annotations

import freemobile_sms


class TestPackageImports:
    """Tests that the package re-exports everything correctly."""

    def test_version(self) -> None:
        """__version__ should be a string."""
        assert isinstance(freemobile_sms.__version__, str)
        assert freemobile_sms.__version__ == "0.1.0"

    def test_all_exports(self) -> None:
        """__all__ should list all public names."""
        expected = {
            "AccountBlockedError",
            "AsyncFreeMobileClient",
            "AuthenticationError",
            "FreeMobileClient",
            "FreeMobileClientError",
            "FreeMobileSettings",
            "FreeMobileStatus",
            "ServerError",
            "SMSResult",
        }
        assert set(freemobile_sms.__all__) == expected

    def test_exception_hierarchy(self) -> None:
        """Custom exceptions should inherit from FreeMobileClientError."""
        assert issubclass(freemobile_sms.AuthenticationError, freemobile_sms.FreeMobileClientError)
        assert issubclass(freemobile_sms.AccountBlockedError, freemobile_sms.FreeMobileClientError)
        assert issubclass(freemobile_sms.ServerError, freemobile_sms.FreeMobileClientError)
        assert issubclass(freemobile_sms.FreeMobileClientError, Exception)

    def test_imports_accessible(self) -> None:
        """All names in __all__ should be importable from the top-level package."""
        for name in freemobile_sms.__all__:
            assert hasattr(freemobile_sms, name), f"{name} not accessible from freemobile_sms"
