"""Contract tests for the workflowy_search_nodes MCP tool."""

import pytest
from fastmcp import FastMCP


class TestSearchNodesContract:
    """Contract tests for node search tool."""

    @pytest.mark.asyncio
    async def test_search_nodes_input_schema(self, _mock_mcp_server: FastMCP) -> None:
        """Test that search_nodes accepts the correct input schema."""
        from workflowy_mcp.server import mcp

        # Get tools from the actual server
        tools = await mcp.get_tools()

        # Find the tool
        assert "workflowy_search_nodes" in tools
        tool = tools["workflowy_search_nodes"]

        assert tool.name == "workflowy_search_nodes"
        assert tool.description is not None

        # Check parameters
        params = tool.parameters
        assert params["type"] == "object"
        assert "query" in params["properties"]
        assert "include_completed" in params["properties"]
        assert params["required"] == ["query"]

    @pytest.mark.asyncio
    async def test_search_nodes_basic(self) -> None:
        """Test basic search_nodes operation."""
        from ..tool_adapters import test_search_nodes

        # This will use mocked client
        result = await test_search_nodes({"query": "test-query"})
        assert result is not None
