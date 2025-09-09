"""Logging middleware for WorkFlowy MCP Server."""

import json
import logging
import time
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("workflowy_mcp")


def log_request_response(func: Callable) -> Callable:
    """Decorator to log MCP tool requests and responses."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        start_time = time.time()
        request_id = f"{func.__name__}_{int(start_time * 1000)}"

        # Log the request
        logger.info(
            "Request received",
            extra={
                "request_id": request_id,
                "tool": func.__name__,
                "args": _sanitize_for_logging(args),
                "kwargs": _sanitize_for_logging(kwargs),
            },
        )

        try:
            # Execute the function
            result = await func(*args, **kwargs)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Log the response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "tool": func.__name__,
                    "execution_time": f"{execution_time:.3f}s",
                    "success": result.get("success", False),
                    "response_size": len(json.dumps(result)),
                },
            )

            return result  # type: ignore[no-any-return]

        except Exception as e:
            # Calculate execution time
            execution_time = time.time() - start_time

            # Log the error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "tool": func.__name__,
                    "execution_time": f"{execution_time:.3f}s",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )

            raise

    return wrapper


def _sanitize_for_logging(data: Any, max_length: int = 200) -> Any:
    """
    Sanitize data for logging by removing sensitive information
    and limiting size.
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Hide sensitive fields
            if key.lower() in ["api_key", "password", "token", "secret"]:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = _sanitize_for_logging(value, max_length)
        return sanitized
    elif isinstance(data, list | tuple):
        return [_sanitize_for_logging(item, max_length) for item in data[:10]]  # Limit array size
    elif isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + "..."
        return data
    else:
        return data


class LoggingMiddleware:
    """Middleware class for structured logging across the MCP server."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize logging middleware."""
        self.logger = logging.getLogger("workflowy_mcp")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        self.request_count = 0
        self.request_times: list[float] = []
        self.tool_usage: dict[str, int] = {}

    def log_request(
        self, tool_name: str, params: dict[str, Any], request_id: str | None = None
    ) -> str:
        """
        Log an incoming request.

        Returns:
            Request ID for tracking
        """
        if request_id is None:
            request_id = f"{tool_name}_{int(time.time() * 1000)}"

        self.request_count += 1
        self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1

        self.logger.info(
            f"Tool request: {tool_name}",
            extra={
                "request_id": request_id,
                "tool": tool_name,
                "params": _sanitize_for_logging(params),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        return request_id

    def log_response(
        self, request_id: str, tool_name: str, response: dict[str, Any], execution_time: float
    ) -> None:
        """Log a response."""
        self.request_times.append(execution_time)

        self.logger.info(
            f"Tool response: {tool_name}",
            extra={
                "request_id": request_id,
                "tool": tool_name,
                "success": response.get("success", False),
                "execution_time": f"{execution_time:.3f}s",
                "response_size": len(json.dumps(response)),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_error(
        self, request_id: str, tool_name: str, error: Exception, execution_time: float
    ) -> None:
        """Log an error."""
        self.logger.error(
            f"Tool error: {tool_name}",
            extra={
                "request_id": request_id,
                "tool": tool_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "execution_time": f"{execution_time:.3f}s",
                "timestamp": datetime.utcnow().isoformat(),
            },
            exc_info=True,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get logging statistics."""
        avg_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        return {
            "total_requests": self.request_count,
            "average_execution_time": f"{avg_time:.3f}s",
            "tool_usage": self.tool_usage.copy(),
            "recent_execution_times": self.request_times[-10:],  # Last 10 requests
        }

    def log_server_start(self, config: dict[str, Any]) -> None:
        """Log server startup."""
        self.logger.info(
            "WorkFlowy MCP Server started",
            extra={
                "config": _sanitize_for_logging(config),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_server_stop(self) -> None:
        """Log server shutdown."""
        stats = self.get_stats()
        self.logger.info(
            "WorkFlowy MCP Server stopped",
            extra={"stats": stats, "timestamp": datetime.utcnow().isoformat()},
        )


# Global logging middleware instance
logging_middleware = LoggingMiddleware()
