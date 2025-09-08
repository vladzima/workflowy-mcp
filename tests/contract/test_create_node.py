"""Contract tests for the workflowy_create_node MCP tool."""

import json
from typing import Any, Dict

import pytest
from fastmcp import FastMCP

from workflowy_mcp.tools.create import workflowy_create_node


class TestCreateNodeContract:
    """Contract tests for node creation tool."""

    @pytest.mark.asyncio
    async def test_create_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that create_node accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            # Register the tool
            mock_mcp_server.tool(workflowy_create_node)
            
            # Verify the input schema
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_create_node"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "name" in schema["properties"]
            assert "note" in schema["properties"]
            assert "parentId" in schema["properties"]
            assert "priority" in schema["properties"]
            assert schema["required"] == ["name"]

    @pytest.mark.asyncio
    async def test_create_node_with_minimal_input(self, sample_create_request: Dict[str, Any]) -> None:
        """Test creating a node with only required fields."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            
            minimal_input = {"name": "Minimal Node"}
            result = await workflowy_create_node(minimal_input)
            
            assert "node" in result
            assert result["node"]["nm"] == "Minimal Node"
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_node_with_full_input(self, sample_create_request: Dict[str, Any]) -> None:
        """Test creating a node with all optional fields."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            
            result = await workflowy_create_node(sample_create_request)
            
            assert "node" in result
            assert result["node"]["nm"] == sample_create_request["name"]
            assert result["node"]["no"] == sample_create_request["note"]
            assert result["node"]["priority"] == sample_create_request["priority"]
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_node_validates_priority(self) -> None:
        """Test that priority validation works correctly."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            
            invalid_input = {
                "name": "Test Node",
                "priority": 5  # Invalid priority (must be 0-3)
            }
            
            with pytest.raises(ValueError, match="priority"):
                await workflowy_create_node(invalid_input)

    @pytest.mark.asyncio
    async def test_create_node_requires_name(self) -> None:
        """Test that name is required."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            
            invalid_input = {
                "note": "Note without name"
            }
            
            with pytest.raises(ValueError, match="name"):
                await workflowy_create_node(invalid_input)

    @pytest.mark.asyncio
    async def test_create_node_handles_api_errors(self) -> None:
        """Test that API errors are handled properly."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            
            # Simulate API error scenario
            input_data = {"name": "Test Node"}
            
            # Mock API to return error
            with pytest.raises(Exception) as exc_info:
                await workflowy_create_node(input_data)
            
            assert "API" in str(exc_info.value)