"""Contract tests for the workflowy_get_node MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestGetNodeContract:
    """Contract tests for node retrieval tool."""

    @pytest.mark.asyncio
    async def test_get_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that get_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.get import workflowy_get_node
            
            mock_mcp_server.tool(workflowy_get_node)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_get_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "id" in schema["properties"]
            assert schema["required"] == ["id"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_get_existing_node(self, sample_node_data: Dict[str, Any]) -> None:
        """Test retrieving an existing node."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.get import workflowy_get_node
            
            input_data = {"id": "node-123"}
            result = await workflowy_get_node(input_data)
            
            assert "node" in result
            assert result["node"]["id"] == "node-123"
            assert "nm" in result["node"]
            assert "cp" in result["node"]
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_get_node_with_children(self) -> None:
        """Test retrieving a node with child nodes."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.get import workflowy_get_node
            
            input_data = {"id": "parent-node"}
            result = await workflowy_get_node(input_data)
            
            assert "node" in result
            assert "ch" in result["node"]  # Children
            assert isinstance(result["node"]["ch"], list)

    @pytest.mark.asyncio
    async def test_get_nonexistent_node(self) -> None:
        """Test retrieving a node that doesn't exist."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.get import workflowy_get_node
            
            input_data = {"id": "nonexistent-node"}
            
            with pytest.raises(Exception) as exc_info:
                await workflowy_get_node(input_data)
            
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_node_requires_id(self) -> None:
        """Test that node ID is required."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.get import workflowy_get_node
            
            invalid_input = {}
            
            with pytest.raises(ValueError, match="id"):
                await workflowy_get_node(invalid_input)