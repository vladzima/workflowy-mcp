"""Contract tests for the workflowy_get_node MCP tool."""

import pytest
from fastmcp import FastMCP


class TestGetNodeContract:
    """Contract tests for node retrieval tool."""

    @pytest.mark.asyncio
    async def test_get_node_input_schema(self, mock_mcp_server: FastMCP) -> None:  # noqa: ARG002
        """Test that get_node accepts the correct input schema."""
        from workflowy_mcp.server import mcp

        # Get tools from the actual server
        tools = await mcp.get_tools()

        # Find the tool
        assert "workflowy_get_node" in tools
        tool = tools["workflowy_get_node"]

        assert tool.name == "workflowy_get_node"
        assert tool.description is not None

        # Check parameters
        params = tool.parameters
        assert params["type"] == "object"
        assert "node_id" in params["properties"]
        assert params["required"] == ["node_id"]

    @pytest.mark.asyncio
    async def test_get_node_basic(self) -> None:
        """Test basic get_node operation."""
        from ..tool_adapters import test_get_node

        # This will use mocked client
        result = await test_get_node({"id": "test-id"})
        assert result is not None
