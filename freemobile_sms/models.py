"""Pydantic models for the Free Mobile SMS API."""

from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel, Field


class FreeMobileStatus(IntEnum):
    """Response status codes from the Free Mobile SMS API.

    See: https://mobile.free.fr/account/mes-options
    """

    OK = 200
    MISSING_PARAMETER = 400
    RATE_LIMITED = 402
    ACCESS_DENIED = 403
    SERVER_ERROR = 500


class SMSResult(BaseModel):
    """Result of an SMS send attempt."""

    success: bool = Field(description="Whether the SMS was sent successfully")
    status_code: int = Field(description="HTTP status code returned by the API")
    message: str = Field(description="Human-readable description of the result")

    @property
    def ok(self) -> bool:
        """Alias for success, mirroring httpx.Response.ok semantics."""
        return self.success
