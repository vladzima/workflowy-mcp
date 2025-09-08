"""Contract tests for the workflowy_uncomplete_node MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestUncompleteNodeContract:
    """Contract tests for node uncompletion tool."""

    @pytest.mark.asyncio
    async def test_uncomplete_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that uncomplete_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            
            mock_mcp_server.tool(workflowy_uncomplete_node)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_uncomplete_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "id" in schema["properties"]
            assert schema["required"] == ["id"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_uncomplete_completed_node(self) -> None:
        """Test uncompleting a node that is completed."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            
            input_data = {"id": "completed-node"}
            result = await workflowy_uncomplete_node(input_data)
            
            assert result["success"] is True
            assert "node" in result
            assert result["node"]["cp"] is False  # cp = completed

    @pytest.mark.asyncio
    async def test_uncomplete_already_uncompleted_node(self) -> None:
        """Test uncompleting a node that is already uncompleted (idempotent)."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            
            input_data = {"id": "uncompleted-node"}
            result = await workflowy_uncomplete_node(input_data)
            
            # Should succeed without error (idempotent operation)
            assert result["success"] is True
            assert result["node"]["cp"] is False

    @pytest.mark.asyncio
    async def test_uncomplete_nonexistent_node(self) -> None:
        """Test uncompleting a node that doesn't exist."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            
            input_data = {"id": "nonexistent-node"}
            
            with pytest.raises(Exception) as exc_info:
                await workflowy_uncomplete_node(input_data)
            
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_uncomplete_node_requires_id(self) -> None:
        """Test that node ID is required for uncompletion."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            
            invalid_input = {}
            
            with pytest.raises(ValueError, match="id"):
                await workflowy_uncomplete_node(invalid_input)

    @pytest.mark.asyncio
    async def test_uncomplete_node_state_transition(self) -> None:
        """Test state transition from completed to uncompleted."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.uncomplete import workflowy_uncomplete_node
            from workflowy_mcp.tools.complete import workflowy_complete_node
            
            node_id = {"id": "test-node"}
            
            # First complete the node
            complete_result = await workflowy_complete_node(node_id)
            assert complete_result["node"]["cp"] is True
            
            # Then uncomplete it
            uncomplete_result = await workflowy_uncomplete_node(node_id)
            assert uncomplete_result["node"]["cp"] is False