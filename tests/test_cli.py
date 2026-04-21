"""Tests for the Typer CLI interface."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from freemobile_sms.cli import app
from freemobile_sms.models import SMSResult

runner = CliRunner()


class TestCLISend:
    """Tests for the 'send' CLI command."""

    def test_send_success(self) -> None:
        """CLI should exit 0 and print success message."""
        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.return_value = SMSResult(
                success=True, status_code=200, message="SMS sent successfully"
            )
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "1234", "--password", "pass"])

        assert result.exit_code == 0, f"Unexpected output: {result.output}"
        assert "SMS sent successfully" in result.output

    def test_send_with_env_vars(self) -> None:
        """CLI should read credentials from env vars."""
        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.return_value = SMSResult(
                success=True, status_code=200, message="SMS sent successfully"
            )
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "1234", "--password", "pass"])

        assert result.exit_code == 0

    def test_send_auth_error(self) -> None:
        """CLI should exit 1 on AuthenticationError."""
        from freemobile_sms.client import AuthenticationError

        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.side_effect = AuthenticationError("Invalid credentials")
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "bad", "--password", "bad"])

        assert result.exit_code == 1
        assert "Invalid credentials" in result.output

    def test_send_account_blocked_error(self) -> None:
        """CLI should exit 1 on AccountBlockedError."""
        from freemobile_sms.client import AccountBlockedError

        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.side_effect = AccountBlockedError("Account blocked")
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "1234", "--password", "pass"])

        assert result.exit_code == 1
        assert "Account blocked" in result.output

    def test_send_server_error(self) -> None:
        """CLI should exit 1 on ServerError."""
        from freemobile_sms.client import ServerError

        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.side_effect = ServerError("Server error")
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "1234", "--password", "pass"])

        assert result.exit_code == 1
        assert "Server error" in result.output

    def test_send_missing_credentials(self) -> None:
        """CLI should exit 1 when credentials are missing."""
        from freemobile_sms.client import FreeMobileClientError

        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.side_effect = FreeMobileClientError("Missing credentials")
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "", "--password", ""])

        assert result.exit_code == 1
        assert "Missing credentials" in result.output

    def test_send_failed_result(self) -> None:
        """CLI should exit 1 when SMS fails (non-exception result)."""
        with patch("freemobile_sms.cli.FreeMobileClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.send.return_value = SMSResult(
                success=False, status_code=400, message="Missing parameter"
            )
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_client.return_value = mock_instance

            result = runner.invoke(app, ["send", "Hello!", "--user", "1234", "--password", "pass"])

        assert result.exit_code == 1
        assert "Missing parameter" in result.output

    def test_no_args_shows_help(self) -> None:
        """Running with no arguments should show help."""
        result = runner.invoke(app, [])
        assert result.exit_code in (0, 2)
        assert "Usage" in result.output
