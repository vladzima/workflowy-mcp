"""Contract tests for the workflowy_update_node MCP tool."""

import json
from typing import Any, Dict
from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import FastMCP


class TestUpdateNodeContract:
    """Contract tests for node update tool."""

    @pytest.mark.asyncio
    async def test_update_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that update_node accepts the correct input schema."""
        from workflowy_mcp.server import mcp
        
        # Get tools from the actual server
        tools = await mcp.get_tools()
        
        # Find the tool
        assert "workflowy_update_node" in tools
        tool = tools["workflowy_update_node"]
        
        assert tool.name == "workflowy_update_node"
        assert tool.description is not None
        
        # Check parameters
        params = tool.parameters
        assert params["type"] == "object"
        assert "node_id" in params["properties"]
        assert "name" in params["properties"]
        assert "note" in params["properties"]
        assert "completed" in params["properties"]
        assert params["required"] == ['node_id']

    @pytest.mark.asyncio
    async def test_update_node_basic(self) -> None:
        """Test basic update_node operation."""
        from tests.tool_adapters import test_update_node
        
        # This will use mocked client
        result = await test_update_node({"id": "test-id"})
        assert result is not None
