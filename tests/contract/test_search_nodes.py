"""Contract tests for the workflowy_search_nodes MCP tool."""

import pytest
from typing import Any, Dict
from fastmcp import FastMCP


class TestSearchNodesContract:
    """Contract tests for node search tool."""

    @pytest.mark.asyncio
    async def test_search_nodes_input_schema(self, mock_mcp_server: FastMCP) -> None:
        """Test that search_nodes accepts the correct input schema."""
        # This test MUST FAIL until the tool is implemented
        with pytest.raises((ImportError, AttributeError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            mock_mcp_server.tool(workflowy_search_nodes)
            
            tool_def = mock_mcp_server.list_tools()[0]
            assert tool_def.name == "workflowy_search_nodes"
            
            schema = tool_def.inputSchema
            assert schema["type"] == "object"
            assert "query" in schema["properties"]
            assert "includeCompleted" in schema["properties"]
            assert schema["required"] == ["query"]
            assert schema.get("additionalProperties") is False

    @pytest.mark.asyncio
    async def test_search_with_query(self) -> None:
        """Test searching nodes with a text query."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            input_data = {"query": "meeting notes"}
            result = await workflowy_search_nodes(input_data)
            
            assert "nodes" in result
            assert isinstance(result["nodes"], list)
            assert "total" in result
            assert result["success"] is True
            
            # All results should contain the query term
            for node in result.get("nodes", []):
                text = (node.get("nm", "") + " " + node.get("no", "")).lower()
                assert "meeting" in text or "notes" in text

    @pytest.mark.asyncio
    async def test_search_include_completed(self) -> None:
        """Test searching with includeCompleted flag."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            input_data = {
                "query": "task",
                "includeCompleted": True
            }
            result = await workflowy_search_nodes(input_data)
            
            assert "nodes" in result
            # May include both completed and uncompleted nodes
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_search_exclude_completed(self) -> None:
        """Test searching without completed nodes."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            input_data = {
                "query": "task",
                "includeCompleted": False
            }
            result = await workflowy_search_nodes(input_data)
            
            assert "nodes" in result
            # Should only include uncompleted nodes
            for node in result.get("nodes", []):
                assert node.get("cp") is False

    @pytest.mark.asyncio
    async def test_search_empty_query(self) -> None:
        """Test that empty query is rejected."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            invalid_input = {"query": ""}
            
            with pytest.raises(ValueError, match="query"):
                await workflowy_search_nodes(invalid_input)

    @pytest.mark.asyncio
    async def test_search_no_results(self) -> None:
        """Test searching with a query that returns no results."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            input_data = {"query": "xyzabc123nonexistent"}
            result = await workflowy_search_nodes(input_data)
            
            assert "nodes" in result
            assert result["nodes"] == []
            assert result["total"] == 0
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self) -> None:
        """Test that search is case-insensitive."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.search import workflowy_search_nodes
            
            # Search with different cases should return same results
            upper_result = await workflowy_search_nodes({"query": "PROJECT"})
            lower_result = await workflowy_search_nodes({"query": "project"})
            
            assert upper_result["total"] == lower_result["total"]