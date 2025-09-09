"""Contract tests for the workflowy_list_nodes MCP tool."""

import json
from typing import Any, Dict
from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import FastMCP


class TestListNodesContract:
    """Contract tests for node listing tool."""

    @pytest.mark.asyncio
    async def test_list_nodes_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that list_nodes accepts the correct input schema."""
        from workflowy_mcp.server import mcp
        
        # Get tools from the actual server
        tools = await mcp.get_tools()
        
        # Find the tool
        assert "workflowy_list_nodes" in tools
        tool = tools["workflowy_list_nodes"]
        
        assert tool.name == "workflowy_list_nodes"
        assert tool.description is not None
        
        # Check parameters
        params = tool.parameters
        assert params["type"] == "object"
        assert "parent_id" in params["properties"]
        assert "include_completed" in params["properties"]
        assert "max_depth" in params["properties"]
        assert "limit" in params["properties"]
        assert "offset" in params["properties"]

    @pytest.mark.asyncio
    async def test_list_nodes_basic(self) -> None:
        """Test basic list_nodes operation."""
        from tests.tool_adapters import test_list_nodes
        
        # This will use mocked client
        result = await test_list_nodes({"id": "test-id"})
        assert result is not None
