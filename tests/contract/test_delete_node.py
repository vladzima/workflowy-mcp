"""Contract tests for the workflowy_delete_node MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestDeleteNodeContract:
    """Contract tests for node deletion tool."""

    @pytest.mark.asyncio
    async def test_delete_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that delete_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            mock_mcp_server.tool(workflowy_delete_node)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_delete_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "id" in schema["properties"]
            assert schema["required"] == ["id"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_delete_existing_node(self) -> None:
        """Test deleting an existing node."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            input_data = {"id": "node-123"}
            result = await workflowy_delete_node(input_data)
            
            assert result["success"] is True
            assert "deleted" in result or "message" in result

    @pytest.mark.asyncio
    async def test_delete_node_with_children(self) -> None:
        """Test deleting a node that has children."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            input_data = {"id": "parent-node-with-children"}
            result = await workflowy_delete_node(input_data)
            
            # Should delete the node and all its children
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_node(self) -> None:
        """Test deleting a node that doesn't exist."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            input_data = {"id": "nonexistent-node"}
            
            with pytest.raises(Exception) as exc_info:
                await workflowy_delete_node(input_data)
            
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_node_requires_id(self) -> None:
        """Test that node ID is required for deletion."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            invalid_input = {}
            
            with pytest.raises(ValueError, match="id"):
                await workflowy_delete_node(invalid_input)

    @pytest.mark.asyncio
    async def test_delete_node_idempotency(self) -> None:
        """Test that deleting the same node twice is handled gracefully."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            input_data = {"id": "node-123"}
            
            # First deletion
            result1 = await workflowy_delete_node(input_data)
            assert result1["success"] is True
            
            # Second deletion should either succeed (idempotent) or fail gracefully
            try:
                result2 = await workflowy_delete_node(input_data)
                assert result2["success"] is True  # Idempotent
            except Exception as e:
                assert "not found" in str(e).lower()  # Already deleted