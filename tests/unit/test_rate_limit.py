"""Unit tests for rate limiting."""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from workflowy_mcp.client.rate_limit import RateLimiter, TokenBucket, AdaptiveRateLimiter


class TestTokenBucket:
    """Test token bucket rate limiting algorithm."""
    
    @pytest.mark.asyncio
    async def test_bucket_initialization(self):
        """Test token bucket initializes with correct capacity."""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        
        assert bucket.capacity == 10
        assert bucket.tokens == 10
        assert bucket.refill_rate == 5
    
    @pytest.mark.asyncio
    async def test_consume_tokens(self):
        """Test consuming tokens from bucket."""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        
        # Consume 3 tokens
        assert await bucket.consume(3) is True
        assert bucket.tokens == 7
        
        # Consume 7 more tokens
        assert await bucket.consume(7) is True
        assert bucket.tokens == 0
        
        # Try to consume when empty (should wait)
        start = time.time()
        assert await bucket.consume(1) is True
        elapsed = time.time() - start
        # Should have waited for refill
        assert elapsed >= 0.1  # At least some delay
    
    @pytest.mark.asyncio
    async def test_token_refill(self):
        """Test tokens refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10)  # 10 tokens per second
        
        # Consume all tokens
        await bucket.consume(10)
        assert bucket.tokens == 0
        
        # Wait for refill
        await asyncio.sleep(0.5)  # Wait 0.5 seconds
        
        # Should have refilled ~5 tokens
        bucket._refill()  # Manually trigger refill
        assert 4 <= bucket.tokens <= 6  # Allow some timing variance
    
    @pytest.mark.asyncio
    async def test_burst_capacity(self):
        """Test burst capacity doesn't exceed limit."""
        bucket = TokenBucket(capacity=5, refill_rate=10)
        
        # Wait to ensure full capacity
        await asyncio.sleep(1)
        bucket._refill()
        
        # Tokens should not exceed capacity
        assert bucket.tokens == 5
    
    @pytest.mark.asyncio
    async def test_concurrent_consumption(self):
        """Test concurrent token consumption."""
        bucket = TokenBucket(capacity=10, refill_rate=5)
        
        # Multiple concurrent consumers
        async def consumer(tokens):
            return await bucket.consume(tokens)
        
        # Try to consume 15 tokens total (more than capacity)
        results = await asyncio.gather(
            consumer(3),
            consumer(3),
            consumer(3),
            consumer(3),
            consumer(3),
            return_exceptions=True
        )
        
        # All should eventually succeed (with waiting)
        assert all(r is True for r in results)


class TestRateLimiter:
    """Test rate limiter implementation."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self):
        """Test rate limit is enforced."""
        limiter = RateLimiter(requests_per_second=10)
        
        # Track request times
        request_times = []
        
        async def make_request():
            await limiter.acquire()
            request_times.append(time.time())
        
        # Make 5 rapid requests
        await asyncio.gather(*[make_request() for _ in range(5)])
        
        # Calculate actual rate
        if len(request_times) > 1:
            duration = request_times[-1] - request_times[0]
            actual_rate = len(request_times) / duration if duration > 0 else float('inf')
            # Should not exceed configured rate (with some tolerance)
            assert actual_rate <= 12  # Allow 20% tolerance
    
    @pytest.mark.asyncio
    async def test_wait_time_calculation(self):
        """Test wait time calculation for rate limiting."""
        limiter = RateLimiter(requests_per_second=2)  # 2 req/sec = 0.5s between requests
        
        # First request should not wait
        wait_time = await limiter.get_wait_time()
        assert wait_time == 0
        
        await limiter.acquire()
        
        # Second request might need to wait
        wait_time = await limiter.get_wait_time()
        assert wait_time >= 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset(self):
        """Test rate limit reset after window."""
        limiter = RateLimiter(
            requests_per_window=5,
            window_seconds=1
        )
        
        # Use all requests
        for _ in range(5):
            await limiter.acquire()
        
        # Should be at limit
        assert limiter.is_at_limit()
        
        # Wait for window to reset
        await asyncio.sleep(1.1)
        
        # Should be able to make requests again
        assert not limiter.is_at_limit()
        await limiter.acquire()  # Should not block


class TestAdaptiveRateLimiter:
    """Test adaptive rate limiting."""
    
    @pytest.mark.asyncio
    async def test_rate_adjustment_on_success(self):
        """Test rate increases on successful requests."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            min_rate=5,
            max_rate=20
        )
        
        initial_rate = limiter.current_rate
        
        # Report successful requests
        for _ in range(10):
            await limiter.report_success()
        
        # Rate should increase
        assert limiter.current_rate > initial_rate
        assert limiter.current_rate <= 20  # Respect max
    
    @pytest.mark.asyncio
    async def test_rate_adjustment_on_rate_limit(self):
        """Test rate decreases on rate limit errors."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            min_rate=5,
            max_rate=20
        )
        
        initial_rate = limiter.current_rate
        
        # Report rate limit error
        await limiter.report_rate_limit()
        
        # Rate should decrease
        assert limiter.current_rate < initial_rate
        assert limiter.current_rate >= 5  # Respect min
    
    @pytest.mark.asyncio
    async def test_rate_recovery(self):
        """Test rate recovers after backing off."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            min_rate=5,
            max_rate=20,
            increase_factor=1.2,
            decrease_factor=0.5
        )
        
        # Cause rate decrease
        await limiter.report_rate_limit()
        decreased_rate = limiter.current_rate
        
        # Report many successes
        for _ in range(20):
            await limiter.report_success()
        
        # Rate should recover
        assert limiter.current_rate > decreased_rate
    
    @pytest.mark.asyncio
    async def test_concurrent_rate_adjustment(self):
        """Test concurrent rate adjustments."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            min_rate=5,
            max_rate=20
        )
        
        # Concurrent success and rate limit reports
        await asyncio.gather(
            limiter.report_success(),
            limiter.report_success(),
            limiter.report_rate_limit(),
            limiter.report_success(),
        )
        
        # Rate should be adjusted (exact value depends on order)
        assert 5 <= limiter.current_rate <= 20
    
    @pytest.mark.asyncio
    async def test_rate_limit_with_retry_after(self):
        """Test handling Retry-After header."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            min_rate=5,
            max_rate=20
        )
        
        # Report rate limit with Retry-After
        await limiter.report_rate_limit(retry_after=5)
        
        # Should respect retry after
        wait_time = await limiter.get_wait_time()
        assert wait_time >= 4  # Allow some timing variance
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self):
        """Test rate limiter tracks statistics."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10,
            track_stats=True
        )
        
        # Make some requests
        await limiter.acquire()
        await limiter.report_success()
        await limiter.acquire()
        await limiter.report_rate_limit()
        
        stats = limiter.get_stats()
        
        assert stats["total_requests"] == 2
        assert stats["successful_requests"] == 1
        assert stats["rate_limited_requests"] == 1
        assert "current_rate" in stats
        assert "average_wait_time" in stats