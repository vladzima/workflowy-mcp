"""Contract tests for the workflowy_uncomplete_node MCP tool."""

import json
from typing import Any, Dict
from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import FastMCP


class TestUncompleteNodeContract:
    """Contract tests for node uncompletion tool."""

    @pytest.mark.asyncio
    async def test_uncomplete_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that uncomplete_node accepts the correct input schema."""
        from workflowy_mcp.server import mcp

        # Get tools from the actual server
        tools = await mcp.get_tools()

        # Find the tool
        assert "workflowy_uncomplete_node" in tools
        tool = tools["workflowy_uncomplete_node"]

        assert tool.name == "workflowy_uncomplete_node"
        assert tool.description is not None

        # Check parameters
        params = tool.parameters
        assert params["type"] == "object"
        assert "node_id" in params["properties"]
        assert params["required"] == ["node_id"]

    @pytest.mark.asyncio
    async def test_uncomplete_node_basic(self) -> None:
        """Test basic uncomplete_node operation."""
        from ..tool_adapters import test_uncomplete_node

        # This will use mocked client
        result = await test_uncomplete_node({"id": "test-id"})
        assert result is not None
