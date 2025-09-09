"""Integration tests for authentication and error handling."""

import os
from unittest.mock import AsyncMock, patch

import pytest


class TestAuthenticationAndErrors:
    """Test authentication flows and error handling."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="load_config function not implemented yet")
    async def test_missing_api_key(self) -> None:
        """Test that missing API key is handled properly."""
        # This test needs load_config function to be implemented
        pass

    @pytest.mark.asyncio
    async def test_invalid_api_key(self) -> None:
        """Test that invalid API key returns proper error."""
        from workflowy_mcp.server import list_nodes

        with (
            patch.dict(os.environ, {"WORKFLOWY_API_KEY": "invalid-key"}),
            patch("workflowy_mcp.client.api_client.httpx.AsyncClient") as mock_client,
        ):
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Unauthorized"}
            mock_client.return_value.get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                # Access the actual function from FunctionTool
                await list_nodes.fn()

            assert "unauthorized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self) -> None:
        """Test that rate limiting is handled with retry logic."""
        from workflowy_mcp.server import list_nodes

        call_count = 0

        async def mock_api_call(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1

            if call_count < 3:
                # Simulate rate limit error
                raise Exception("Rate limit exceeded")
            else:
                # Success after retries
                return {"nodes": [], "total": 0, "success": True}

        with patch("workflowy_mcp.client.api_client.WorkFlowyClient.list_nodes", mock_api_call):
            result = await list_nodes.fn()
            assert result["success"] is True
            assert call_count == 3  # Should retry twice

    @pytest.mark.asyncio
    async def test_network_error_handling(self) -> None:
        """Test handling of network errors."""
        import httpx

        from workflowy_mcp.server import get_node

        with patch("workflowy_mcp.client.api_client.httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(Exception) as exc_info:
                await get_node.fn(node_id="test-node")

            assert (
                "network" in str(exc_info.value).lower()
                or "connection" in str(exc_info.value).lower()
            )

    @pytest.mark.asyncio
    async def test_timeout_handling(self) -> None:
        """Test handling of request timeouts."""
        import httpx

        from workflowy_mcp.server import create_node

        with patch("workflowy_mcp.client.api_client.httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(Exception) as exc_info:
                await create_node.fn(name="Test Node")

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self) -> None:
        """Test handling of malformed API responses."""
        from workflowy_mcp.server import get_node

        with patch("workflowy_mcp.client.api_client.httpx.AsyncClient.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"invalid": "response"}  # Missing expected fields
            mock_get.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await get_node.fn(node_id="test-node")

            assert (
                "response" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()
            )

    @pytest.mark.asyncio
    async def test_server_error_handling(self) -> None:
        """Test handling of 5xx server errors."""
        from workflowy_mcp.server import delete_node

        with patch("workflowy_mcp.client.api_client.httpx.AsyncClient.delete") as mock_delete:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_delete.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await delete_node.fn(node_id="test-node")

            assert "server" in str(exc_info.value).lower() or "500" in str(exc_info.value)
