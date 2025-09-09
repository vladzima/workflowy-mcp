"""Error handling middleware for WorkFlowy MCP Server."""

import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any

import httpx

from workflowy_mcp.models.errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    WorkFlowyError,
)


def error_handler(func: Callable) -> Callable:
    """Decorator to handle errors in MCP tool functions."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            return await func(*args, **kwargs)  # type: ignore[no-any-return]
        except ValidationError as e:
            return {
                "success": False,
                "error": "validation_error",
                "message": str(e),
                "field": getattr(e, "field", None),
                "constraint": getattr(e, "constraint", None),
            }
        except AuthenticationError as e:
            return {
                "success": False,
                "error": "authentication_error",
                "message": str(e),
                "realm": getattr(e, "realm", "WorkFlowy API"),
            }
        except RateLimitError as e:
            return {
                "success": False,
                "error": "rate_limit_error",
                "message": str(e),
                "retry_after": getattr(e, "retry_after", 60),
            }
        except APIError as e:
            return {
                "success": False,
                "error": "api_error",
                "message": str(e),
                "status_code": getattr(e, "status_code", None),
            }
        except httpx.NetworkError as e:
            return {
                "success": False,
                "error": "network_error",
                "message": f"Network connection failed: {str(e)}",
            }
        except httpx.TimeoutException as e:
            return {
                "success": False,
                "error": "timeout_error",
                "message": f"Request timed out: {str(e)}",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": "http_error",
                "message": f"HTTP {e.response.status_code}: {str(e)}",
                "status_code": e.response.status_code,
            }
        except WorkFlowyError as e:
            return {"success": False, "error": "workflowy_error", "message": str(e)}
        except Exception as e:
            # Log the full traceback for debugging
            traceback.print_exc()
            return {
                "success": False,
                "error": "internal_error",
                "message": f"An unexpected error occurred: {str(e)}",
            }

    return wrapper


class ErrorMiddleware:
    """Middleware class for handling errors across the MCP server."""

    def __init__(self) -> None:
        """Initialize error middleware."""
        self.error_count = 0
        self.error_types: dict[str, int] = {}

    def track_error(self, error_type: str) -> None:
        """Track error occurrences for monitoring."""
        self.error_count += 1
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1

    def get_error_stats(self) -> dict[str, Any]:
        """Get error statistics."""
        return {"total_errors": self.error_count, "error_types": self.error_types.copy()}

    def reset_stats(self) -> None:
        """Reset error statistics."""
        self.error_count = 0
        self.error_types.clear()

    async def handle_error(self, error: Exception, context: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an error with context information.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred

        Returns:
            Formatted error response
        """
        error_type = type(error).__name__
        self.track_error(error_type)

        # Add context to the response
        response = {
            "success": False,
            "error": error_type.lower(),
            "message": str(error),
            "context": context,
        }

        # Add specific error details based on type
        if isinstance(error, httpx.HTTPStatusError):
            response["status_code"] = error.response.status_code
            response["response_body"] = error.response.text[:500]  # Limit size
        elif isinstance(error, RateLimitError):
            response["retry_after"] = getattr(error, "retry_after", 60)
        elif isinstance(error, ValidationError):
            response["field"] = getattr(error, "field", None)
            response["value"] = getattr(error, "value", None)

        return response


# Global middleware instance
error_middleware = ErrorMiddleware()
