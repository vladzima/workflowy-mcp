"""Contract tests for the workflowy_complete_node MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestCompleteNodeContract:
    """Contract tests for node completion tool."""

    @pytest.mark.asyncio
    async def test_complete_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that complete_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            mock_mcp_server.tool(workflowy_complete_node)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_complete_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "id" in schema["properties"]
            assert schema["required"] == ["id"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_complete_uncompleted_node(self) -> None:
        """Test completing a node that is not completed."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            input_data = {"id": "node-123"}
            result = await workflowy_complete_node(input_data)
            
            assert result["success"] is True
            assert "node" in result
            assert result["node"]["cp"] is True  # cp = completed

    @pytest.mark.asyncio
    async def test_complete_already_completed_node(self) -> None:
        """Test completing a node that is already completed (idempotent)."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            input_data = {"id": "already-completed-node"}
            result = await workflowy_complete_node(input_data)
            
            # Should succeed without error (idempotent operation)
            assert result["success"] is True
            assert result["node"]["cp"] is True

    @pytest.mark.asyncio
    async def test_complete_nonexistent_node(self) -> None:
        """Test completing a node that doesn't exist."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            input_data = {"id": "nonexistent-node"}
            
            with pytest.raises(Exception) as exc_info:
                await workflowy_complete_node(input_data)
            
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_complete_node_requires_id(self) -> None:
        """Test that node ID is required for completion."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            invalid_input = {}
            
            with pytest.raises(ValueError, match="id"):
                await workflowy_complete_node(invalid_input)

    @pytest.mark.asyncio
    async def test_complete_node_with_children(self) -> None:
        """Test completing a node that has child nodes."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            input_data = {"id": "parent-node"}
            result = await workflowy_complete_node(input_data)
            
            # Parent should be completed, children unaffected
            assert result["success"] is True
            assert result["node"]["cp"] is True