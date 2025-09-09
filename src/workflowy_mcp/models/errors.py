"""Error response models and exception classes."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response for all operations."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: dict[str, Any] | None = Field(None, description="Additional error context")
    success: bool = Field(False, description="Always false for errors")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "error": "Node not found",
                "code": "NODE_NOT_FOUND",
                "details": {"node_id": "invalid-123"},
                "success": False,
            }
        }


class APIError(Exception):
    """Base API error class (alias for compatibility)."""

    pass


class WorkFlowyError(Exception):
    """Base exception for WorkFlowy MCP errors."""

    def __init__(
        self, message: str, code: str = "WORKFLOWY_ERROR", details: dict[str, Any] | None = None
    ):
        """Initialize the error."""
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_response(self) -> ErrorResponse:
        """Convert exception to error response."""
        return ErrorResponse(
            error=self.message, code=self.code, details=self.details, success=False
        )


class AuthenticationError(WorkFlowyError):
    """Raised when authentication fails."""

    def __init__(
        self, message: str = "Authentication failed", details: dict[str, Any] | None = None
    ):
        """Initialize authentication error."""
        super().__init__(message, "AUTH_ERROR", details)


class NodeNotFoundError(WorkFlowyError):
    """Raised when a requested node doesn't exist."""

    def __init__(self, node_id: str, message: str | None = None):
        """Initialize node not found error."""
        msg = message or f"Node with ID '{node_id}' not found"
        super().__init__(msg, "NODE_NOT_FOUND", {"node_id": node_id})


class ValidationError(WorkFlowyError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None):
        """Initialize validation error."""
        details = {"field": field} if field else {}
        super().__init__(message, "VALIDATION_ERROR", details)


class RateLimitError(WorkFlowyError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        """Initialize rate limit error."""
        message = "Rate limit exceeded"
        details = {}
        if retry_after:
            message += f". Retry after {retry_after} seconds"
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class NetworkError(WorkFlowyError):
    """Raised when network operations fail."""

    def __init__(
        self, message: str = "Network error occurred", details: dict[str, Any] | None = None
    ):
        """Initialize network error."""
        super().__init__(message, "NETWORK_ERROR", details)


class TimeoutError(WorkFlowyError):
    """Raised when operations timeout."""

    def __init__(self, operation: str | None = None):
        """Initialize timeout error."""
        message = f"Operation '{operation}' timed out" if operation else "Request timed out"
        super().__init__(message, "TIMEOUT_ERROR", {"operation": operation} if operation else {})
