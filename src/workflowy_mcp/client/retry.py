"""Retry logic with exponential backoff for API requests."""

import asyncio
import logging
import random
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from ..models.errors import NetworkError, RateLimitError, TimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryHandler:
    """Handle retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry handler."""
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        # Exponential backoff
        delay = min(self.base_delay * (self.exponential_base**attempt), self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay

    async def execute_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a function with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Use retry_after if provided, otherwise exponential backoff
                    delay = e.details.get("retry_after", self.calculate_delay(attempt))
                    logger.warning(
                        f"Rate limit hit, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max retries reached for rate limit error")
                    raise

            except (NetworkError, TimeoutError) as e:
                last_exception = e  # type: ignore[assignment]
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"Network/timeout error, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries reached for network error: {str(e)}")
                    raise

            except Exception as e:
                # Don't retry on other exceptions
                logger.error(f"Non-retryable error: {str(e)}")
                raise

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry logic error")


def with_retry(
    max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
) -> Callable[..., Any]:
    """Decorator to add retry logic to async functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            handler = RetryHandler(
                max_retries=max_retries, base_delay=base_delay, max_delay=max_delay
            )
            return await handler.execute_with_retry(func, *args, **kwargs)

        return wrapper

    return decorator
