"""Rate limiting handler for WorkFlowy API requests."""

import asyncio
import logging
import time
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: int | None = None,
        retry_after_header: bool = True,
    ):
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum sustained request rate
            burst_size: Maximum burst capacity (defaults to requests_per_second)
            retry_after_header: Whether to respect Retry-After headers
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size or int(requests_per_second)
        self.retry_after_header = retry_after_header

        # Token bucket implementation
        self.tokens = float(self.burst_size)
        self.max_tokens = float(self.burst_size)
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

        # Request history for sliding window
        self.request_times: deque[float] = deque(maxlen=100)

        # Track retry-after if we hit rate limits
        self.retry_after_until: float | None = None

    async def acquire(self, cost: float = 1.0) -> None:
        """Acquire permission to make a request.

        Args:
            cost: Number of tokens to consume (default 1.0)
        """
        async with self.lock:
            # Check if we're in a retry-after period
            if self.retry_after_until:
                wait_time = self.retry_after_until - time.time()
                if wait_time > 0:
                    logger.info(f"Rate limited, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    self.retry_after_until = None

            # Update token bucket
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Add tokens based on elapsed time
            tokens_to_add = elapsed * self.requests_per_second
            self.tokens = min(self.tokens + tokens_to_add, self.max_tokens)

            # Wait if not enough tokens
            if self.tokens < cost:
                wait_time = (cost - self.tokens) / self.requests_per_second
                logger.debug(f"Rate limiting: waiting {wait_time:.3f}s")
                await asyncio.sleep(wait_time)

                # Update tokens after waiting
                now = time.monotonic()
                elapsed = now - self.last_update
                self.last_update = now
                tokens_to_add = elapsed * self.requests_per_second
                self.tokens = min(self.tokens + tokens_to_add, self.max_tokens)

            # Consume tokens
            self.tokens -= cost

            # Track request time
            self.request_times.append(time.time())

    def set_retry_after(self, seconds: int) -> None:
        """Set retry-after period from server response.

        Args:
            seconds: Number of seconds to wait before retrying
        """
        if self.retry_after_header:
            self.retry_after_until = time.time() + seconds
            logger.warning(f"Server requested retry after {seconds}s")

    def get_current_rate(self) -> float:
        """Get the current request rate (requests per second)."""
        if len(self.request_times) < 2:
            return 0.0

        now = time.time()
        # Filter requests in the last minute
        recent_requests = [t for t in self.request_times if now - t < 60]

        if len(recent_requests) < 2:
            return 0.0

        time_span = now - recent_requests[0]
        if time_span > 0:
            return float(len(recent_requests) / time_span)
        return 0.0

    def reset(self) -> None:
        """Reset the rate limiter state."""
        self.tokens = float(self.max_tokens)
        self.last_update = time.monotonic()
        self.request_times.clear()
        self.retry_after_until = None


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts based on server responses."""

    def __init__(
        self,
        initial_rate: float = 10.0,
        min_rate: float = 1.0,
        max_rate: float = 100.0,
        **kwargs: Any,
    ):
        """Initialize adaptive rate limiter."""
        super().__init__(requests_per_second=initial_rate, **kwargs)
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.consecutive_successes = 0
        self.consecutive_failures = 0

    def on_success(self) -> None:
        """Called when a request succeeds."""
        self.consecutive_successes += 1
        self.consecutive_failures = 0

        # Gradually increase rate after consecutive successes
        if self.consecutive_successes >= 10:
            new_rate = min(self.requests_per_second * 1.1, self.max_rate)
            if new_rate != self.requests_per_second:
                logger.info(f"Increasing rate limit to {new_rate:.1f} req/s")
                self.requests_per_second = new_rate
                self.consecutive_successes = 0

    def on_rate_limit(self, retry_after: int | None = None) -> None:
        """Called when we hit a rate limit."""
        self.consecutive_failures += 1
        self.consecutive_successes = 0

        # Reduce rate on rate limit
        new_rate = max(self.requests_per_second * 0.5, self.min_rate)
        if new_rate != self.requests_per_second:
            logger.warning(f"Reducing rate limit to {new_rate:.1f} req/s")
            self.requests_per_second = new_rate

        if retry_after:
            self.set_retry_after(retry_after)
