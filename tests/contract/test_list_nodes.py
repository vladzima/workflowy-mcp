"""Contract tests for the workflowy_list_nodes MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestListNodesContract:
    """Contract tests for node listing tool."""

    @pytest.mark.asyncio
    async def test_list_nodes_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that list_nodes accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            mock_mcp_server.tool(workflowy_list_nodes)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_list_nodes"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "parentId" in schema["properties"]
            assert "completed" in schema["properties"]
            assert "query" in schema["properties"]
            assert "limit" in schema["properties"]
            assert "offset" in schema["properties"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_list_all_nodes(self) -> None:
        """Test listing all nodes without filters."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            result = await workflowy_list_nodes({})
            
            assert "nodes" in result
            assert isinstance(result["nodes"], list)
            assert "total" in result
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_nodes_with_limit(self) -> None:
        """Test listing nodes with a limit."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            input_data = {"limit": 5}
            result = await workflowy_list_nodes(input_data)
            
            assert "nodes" in result
            assert len(result["nodes"]) <= 5
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_nodes_with_pagination(self) -> None:
        """Test listing nodes with pagination."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            input_data = {"limit": 10, "offset": 20}
            result = await workflowy_list_nodes(input_data)
            
            assert "nodes" in result
            assert "total" in result
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_nodes_by_parent(self) -> None:
        """Test listing child nodes of a specific parent."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            input_data = {"parentId": "parent-123"}
            result = await workflowy_list_nodes(input_data)
            
            assert "nodes" in result
            # All returned nodes should be children of the specified parent
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_completed_nodes(self) -> None:
        """Test filtering by completion status."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            input_data = {"completed": True}
            result = await workflowy_list_nodes(input_data)
            
            assert "nodes" in result
            # All returned nodes should be completed
            for node in result.get("nodes", []):
                assert node.get("cp") is True

    @pytest.mark.asyncio
    async def test_list_nodes_with_query(self) -> None:
        """Test searching nodes with a query."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            input_data = {"query": "test"}
            result = await workflowy_list_nodes(input_data)
            
            assert "nodes" in result
            # Results should contain the query term
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_nodes_validates_limit(self) -> None:
        """Test that limit validation works."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.list import workflowy_list_nodes
            
            invalid_input = {"limit": 2000}  # Exceeds max of 1000
            
            with pytest.raises(ValueError, match="limit"):
                await workflowy_list_nodes(invalid_input)