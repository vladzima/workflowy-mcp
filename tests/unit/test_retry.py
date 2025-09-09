"""Unit tests for retry logic."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import httpx

from workflowy_mcp.client.retry import RetryHandler, RetryConfig


class TestRetryHandler:
    """Test retry handler functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_first_attempt(self):
        """Test that successful requests don't retry."""
        config = RetryConfig(max_retries=3)
        handler = RetryHandler(config)
        
        mock_func = AsyncMock(return_value={"success": True})
        
        result = await handler.execute(mock_func)
        
        assert result == {"success": True}
        assert mock_func.call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_network_error(self):
        """Test retry on network errors."""
        config = RetryConfig(max_retries=3, initial_delay=0.01)
        handler = RetryHandler(config)
        
        # Fail twice, then succeed
        mock_func = AsyncMock(side_effect=[
            httpx.NetworkError("Connection failed"),
            httpx.NetworkError("Connection failed"),
            {"success": True}
        ])
        
        result = await handler.execute(mock_func)
        
        assert result == {"success": True}
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Test retry on timeout errors."""
        config = RetryConfig(max_retries=2, initial_delay=0.01)
        handler = RetryHandler(config)
        
        # Timeout once, then succeed
        mock_func = AsyncMock(side_effect=[
            httpx.TimeoutException("Request timed out"),
            {"success": True}
        ])
        
        result = await handler.execute(mock_func)
        
        assert result == {"success": True}
        assert mock_func.call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_on_5xx_errors(self):
        """Test retry on server errors (5xx)."""
        config = RetryConfig(max_retries=3, initial_delay=0.01)
        handler = RetryHandler(config)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 503
        
        # Fail with 503 twice, then succeed
        mock_func = AsyncMock(side_effect=[
            httpx.HTTPStatusError("Service unavailable", request=None, response=mock_response),
            httpx.HTTPStatusError("Service unavailable", request=None, response=mock_response),
            {"success": True}
        ])
        
        result = await handler.execute(mock_func)
        
        assert result == {"success": True}
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_errors(self):
        """Test no retry on client errors (4xx)."""
        config = RetryConfig(max_retries=3)
        handler = RetryHandler(config)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        mock_func = AsyncMock(
            side_effect=httpx.HTTPStatusError("Not found", request=None, response=mock_response)
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await handler.execute(mock_func)
        
        # Should not retry on 4xx
        assert mock_func.call_count == 1
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that retries stop after max attempts."""
        config = RetryConfig(max_retries=2, initial_delay=0.01)
        handler = RetryHandler(config)
        
        mock_func = AsyncMock(
            side_effect=httpx.NetworkError("Connection failed")
        )
        
        with pytest.raises(httpx.NetworkError):
            await handler.execute(mock_func)
        
        # Initial attempt + 2 retries = 3 total
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff delays."""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2
        )
        handler = RetryHandler(config)
        
        # Track delays
        delays = []
        original_sleep = asyncio.sleep
        
        async def mock_sleep(delay):
            delays.append(delay)
            return await original_sleep(0.001)  # Speed up test
        
        mock_func = AsyncMock(
            side_effect=httpx.NetworkError("Connection failed")
        )
        
        with pytest.mock.patch('asyncio.sleep', mock_sleep):
            with pytest.raises(httpx.NetworkError):
                await handler.execute(mock_func)
        
        # Check delays increase exponentially
        assert len(delays) == 3  # One delay per retry
        assert delays[0] >= 0.1  # First delay
        assert delays[1] >= delays[0] * 1.5  # Should increase
        assert delays[2] >= delays[1] * 1.5  # Should increase more
        assert all(d <= 1.0 for d in delays)  # Respect max_delay
    
    @pytest.mark.asyncio
    async def test_retry_with_rate_limit_header(self):
        """Test retry respects Retry-After header."""
        config = RetryConfig(max_retries=2, initial_delay=0.01)
        handler = RetryHandler(config)
        
        # Create mock response with Retry-After header
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        
        mock_func = AsyncMock(side_effect=[
            httpx.HTTPStatusError("Rate limited", request=None, response=mock_response),
            {"success": True}
        ])
        
        # Track sleep calls
        sleep_calls = []
        original_sleep = asyncio.sleep
        
        async def mock_sleep(delay):
            sleep_calls.append(delay)
            return await original_sleep(0.001)
        
        with pytest.mock.patch('asyncio.sleep', mock_sleep):
            result = await handler.execute(mock_func)
        
        assert result == {"success": True}
        assert mock_func.call_count == 2
        # Should respect Retry-After header
        assert any(s >= 1.0 for s in sleep_calls)
    
    @pytest.mark.asyncio
    async def test_custom_retry_condition(self):
        """Test custom retry condition function."""
        def custom_condition(exception):
            # Only retry on specific message
            return isinstance(exception, Exception) and "retry_me" in str(exception)
        
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.01,
            retry_condition=custom_condition
        )
        handler = RetryHandler(config)
        
        # Should retry this
        mock_func1 = AsyncMock(side_effect=[
            Exception("retry_me please"),
            {"success": True}
        ])
        
        result = await handler.execute(mock_func1)
        assert result == {"success": True}
        assert mock_func1.call_count == 2
        
        # Should not retry this
        mock_func2 = AsyncMock(side_effect=Exception("do not retry"))
        
        with pytest.raises(Exception, match="do not retry"):
            await handler.execute(mock_func2)
        
        assert mock_func2.call_count == 1