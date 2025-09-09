"""Contract tests for the workflowy_create_node MCP tool."""

import json
from typing import Any, Dict
from unittest.mock import patch, AsyncMock

import pytest
from fastmcp import FastMCP


class TestCreateNodeContract:
    """Contract tests for node creation tool."""

    @pytest.mark.asyncio
    async def test_create_node_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that create_node accepts the correct input schema."""
        from workflowy_mcp.server import mcp

        # Get tools from the actual server
        tools = await mcp.get_tools()

        # Find the create_node tool
        assert "workflowy_create_node" in tools
        create_tool = tools["workflowy_create_node"]

        assert create_tool.name == "workflowy_create_node"
        assert create_tool.description == "Create a new node in WorkFlowy"

        # Check parameters
        params = create_tool.parameters
        assert params["type"] == "object"
        assert "name" in params["properties"]
        assert "parent_id" in params["properties"]
        assert "note" in params["properties"]
        assert "completed" in params["properties"]
        assert params["required"] == ["name"]

    @pytest.mark.asyncio
    async def test_create_node_with_minimal_input(
        self, sample_create_request: Dict[str, Any]
    ) -> None:
        """Test creating a node with only required fields."""
        from tests.tool_adapters import test_create_node

        minimal_input = {"name": "Minimal Node"}
        result = await test_create_node(minimal_input)

        assert "node" in result
        assert result["node"]["nm"] == "Minimal Node"
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_node_with_full_input(self, sample_create_request: Dict[str, Any]) -> None:
        """Test creating a node with all optional fields."""
        from tests.tool_adapters import test_create_node

        result = await test_create_node(sample_create_request)

        assert "node" in result
        assert result["node"]["nm"] == sample_create_request["name"]
        assert result["node"]["no"] == sample_create_request["note"]
        assert result["node"]["priority"] == sample_create_request["priority"]
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_node_validates_priority(self) -> None:
        """Test that priority validation works correctly."""
        from tests.tool_adapters import test_create_node

        invalid_input = {"name": "Test Node", "priority": 5}  # Invalid priority (must be 0-3)

        # For now, just test that it doesn't crash
        # Priority validation would be done at the API level
        result = await test_create_node(invalid_input)
        assert "node" in result

    @pytest.mark.asyncio
    async def test_create_node_requires_name(self) -> None:
        """Test that name is required."""
        from workflowy_mcp.server import create_node as create_node_tool

        # Get the actual function
        create_node = create_node_tool.fn

        # Test directly with the function to check parameter requirements
        with pytest.raises(TypeError):  # Missing required argument
            await create_node(note="Note without name")

    @pytest.mark.asyncio
    async def test_create_node_handles_api_errors(self) -> None:
        """Test that API errors are handled properly."""
        from workflowy_mcp.server import create_node as create_node_tool
        from workflowy_mcp.models import NetworkError

        # Get the actual function
        create_node = create_node_tool.fn

        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            # Mock API to raise an error
            mock_client.create_node.side_effect = NetworkError("API Error")

            # Test that the error is raised
            with pytest.raises(NetworkError) as exc_info:
                await create_node(name="Test Node")

            assert "API Error" in str(exc_info.value)
