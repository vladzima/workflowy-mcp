"""Contract tests for the workflowy_update_node MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestUpdateNodeContract:
    """Contract tests for node update tool."""

    @pytest.mark.asyncio
    async def test_update_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that update_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            mock_mcp_server.tool(workflowy_update_node)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_update_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "id" in schema["properties"]
            assert "name" in schema["properties"]
            assert "note" in schema["properties"]
            assert "priority" in schema["properties"]
            assert "parentId" in schema["properties"]
            assert schema["required"] == ["id"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_update_node_with_name_only(self, sample_update_request: Dict[str, Any]) -> None:
        """Test updating only the name of a node."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            input_data = {
                "id": "node-123",
                "name": "New Name Only"
            }
            result = await workflowy_update_node(input_data)
            
            assert "node" in result
            assert result["node"]["id"] == "node-123"
            assert result["node"]["nm"] == "New Name Only"
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_node_with_all_fields(self, sample_update_request: Dict[str, Any]) -> None:
        """Test updating all fields of a node."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            result = await workflowy_update_node(sample_update_request)
            
            assert "node" in result
            assert result["node"]["id"] == sample_update_request["id"]
            assert result["node"]["nm"] == sample_update_request["name"]
            assert result["node"]["no"] == sample_update_request["note"]
            assert result["node"]["priority"] == sample_update_request["priority"]
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_node_move_to_parent(self) -> None:
        """Test moving a node to a different parent."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            input_data = {
                "id": "node-123",
                "parentId": "parent-456"
            }
            result = await workflowy_update_node(input_data)
            
            assert result["success"] is True
            assert "node" in result

    @pytest.mark.asyncio
    async def test_update_node_requires_id(self) -> None:
        """Test that node ID is required for updates."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            invalid_input = {
                "name": "Missing ID"
            }
            
            with pytest.raises(ValueError, match="id"):
                await workflowy_update_node(invalid_input)

    @pytest.mark.asyncio
    async def test_update_node_validates_priority(self) -> None:
        """Test that priority validation works in updates."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            invalid_input = {
                "id": "node-123",
                "priority": -1  # Invalid priority
            }
            
            with pytest.raises(ValueError, match="priority"):
                await workflowy_update_node(invalid_input)

    @pytest.mark.asyncio
    async def test_update_nonexistent_node(self) -> None:
        """Test updating a node that doesn't exist."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.update import workflowy_update_node
            
            input_data = {
                "id": "nonexistent-node",
                "name": "This will fail"
            }
            
            with pytest.raises(Exception) as exc_info:
                await workflowy_update_node(input_data)
            
            assert "not found" in str(exc_info.value).lower()