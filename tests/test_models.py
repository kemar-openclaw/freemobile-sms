"""Tests for the Free Mobile SMS API models."""

from __future__ import annotations

from freemobile_sms.models import FreeMobileStatus, SMSResult


class TestFreeMobileStatus:
    """Tests for the FreeMobileStatus enum."""

    def test_status_values_match_docs(self) -> None:
        """Status codes should match the official Free Mobile API documentation."""
        assert FreeMobileStatus.OK == 200
        assert FreeMobileStatus.MISSING_PARAMETER == 400
        assert FreeMobileStatus.RATE_LIMITED == 402
        assert FreeMobileStatus.ACCESS_DENIED == 403
        assert FreeMobileStatus.SERVER_ERROR == 500

    def test_all_statuses_present(self) -> None:
        """All five Free Mobile statuses should exist."""
        assert len(FreeMobileStatus) == 5


class TestSMSResult:
    """Tests for the SMSResult model."""

    def test_successful_result(self) -> None:
        """A successful result should have ok=True."""
        result = SMSResult(success=True, status_code=200, message="SMS sent successfully")
        assert result.success is True
        assert result.ok is True
        assert result.status_code == 200

    def test_failed_result(self) -> None:
        """A failed result should have ok=False."""
        result = SMSResult(success=False, status_code=400, message="Missing parameter")
        assert result.success is False
        assert result.ok is False
        assert result.status_code == 400

    def test_ok_property_is_alias(self) -> None:
        """The ok property should mirror success."""
        result = SMSResult(success=True, status_code=200, message="ok")
        assert result.ok == result.success

    def test_model_serialization(self) -> None:
        """SMSResult should serialize and deserialize correctly."""
        result = SMSResult(success=True, status_code=200, message="ok")
        data = result.model_dump()
        restored = SMSResult(**data)
        assert restored == result
