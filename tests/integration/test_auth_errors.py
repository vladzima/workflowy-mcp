"""Integration tests for authentication and error handling."""

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
    async def test_invalid_api_key(self, mock_workflowy_client) -> None:
        """Test that invalid API key returns proper error."""
        from workflowy_mcp.server import list_nodes

        # Configure mock to raise authentication error
        mock_workflowy_client.list_nodes.side_effect = Exception("Unauthorized: Invalid API key")

        with pytest.raises(Exception) as exc_info:
            await list_nodes.fn()

        assert "unauthorized" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Rate limit retry logic not implemented in server yet")
    async def test_rate_limit_handling(self, mock_workflowy_client) -> None:
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
                # Success after retries - return what client.list_nodes returns
                return ([], 0)  # Client returns tuple of (nodes, total)

        mock_workflowy_client.list_nodes.side_effect = mock_api_call
        result = await list_nodes.fn()
        assert result["nodes"] == []
        assert result["total"] == 0
        assert call_count == 3  # Should retry twice

    @pytest.mark.asyncio
    async def test_network_error_handling(self, mock_workflowy_client) -> None:
        """Test handling of network errors."""
        from workflowy_mcp.server import get_node

        mock_workflowy_client.get_node.side_effect = Exception("Network error: Connection failed")

        with pytest.raises(Exception) as exc_info:
            await get_node.fn(node_id="test-node")

        assert (
            "network" in str(exc_info.value).lower() or "connection" in str(exc_info.value).lower()
        )

    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_workflowy_client) -> None:
        """Test handling of request timeouts."""
        from workflowy_mcp.server import create_node

        mock_workflowy_client.create_node.side_effect = Exception("Request timed out")

        with pytest.raises(Exception) as exc_info:
            await create_node.fn(name="Test Node")

        assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, mock_workflowy_client) -> None:
        """Test handling of malformed API responses."""
        from workflowy_mcp.server import get_node

        mock_workflowy_client.get_node.side_effect = Exception("Invalid response format")

        with pytest.raises(Exception) as exc_info:
            await get_node.fn(node_id="test-node")

        assert "response" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_server_error_handling(self, mock_workflowy_client) -> None:
        """Test handling of 5xx server errors."""
        from workflowy_mcp.server import delete_node

        mock_workflowy_client.delete_node.side_effect = Exception("Internal server error: 500")

        with pytest.raises(Exception) as exc_info:
            await delete_node.fn(node_id="test-node")

        assert "server" in str(exc_info.value).lower() or "500" in str(exc_info.value)
