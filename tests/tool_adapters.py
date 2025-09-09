"""Adapters to make MCP tools testable."""

import time
from typing import Any
from unittest.mock import AsyncMock, patch

from workflowy_mcp.models import WorkFlowyNode
from workflowy_mcp.server import (
    complete_node as complete_node_tool,
)
from workflowy_mcp.server import (
    create_node as create_node_tool,
)
from workflowy_mcp.server import (
    delete_node as delete_node_tool,
)
from workflowy_mcp.server import (
    get_node as get_node_tool,
)
from workflowy_mcp.server import (
    list_nodes as list_nodes_tool,
)
from workflowy_mcp.server import (
    search_nodes as search_nodes_tool,
)
from workflowy_mcp.server import (
    uncomplete_node as uncomplete_node_tool,
)
from workflowy_mcp.server import (
    update_node as update_node_tool,
)

# Get the actual functions from the tools
create_node = create_node_tool.fn
update_node = update_node_tool.fn
get_node = get_node_tool.fn
list_nodes = list_nodes_tool.fn
delete_node = delete_node_tool.fn
complete_node = complete_node_tool.fn
uncomplete_node = uncomplete_node_tool.fn
search_nodes = search_nodes_tool.fn


# Create wrapper functions that can be tested
async def test_create_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for create_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        # Clamp priority to valid range for testing
        priority = data.get("priority", 0)
        if priority is not None and priority > 3:
            priority = 3

        mock_node = WorkFlowyNode(
            id="new-node-id",
            nm=data.get("name", ""),
            no=data.get("note"),
            cp=data.get("completed", False),
            priority=priority,
            created=int(time.time()),
            modified=int(time.time()),
        )
        mock_client.create_node.return_value = mock_node

        # Call the actual function
        result = await create_node(
            name=data["name"],
            parent_id=data.get("parentId"),
            note=data.get("note"),
            _completed=data.get("completed", False),
        )

        return {"success": True, "node": result.model_dump()}


async def test_update_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for update_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_node = WorkFlowyNode(
            id=data["id"],
            nm=data.get("name", "Updated Node"),
            no=data.get("note"),
            cp=data.get("completed", False),
            priority=data.get("priority", 0),
            created=int(time.time()),
            modified=int(time.time()),
        )
        mock_client.update_node.return_value = mock_node

        # Call the actual function
        result = await update_node(
            node_id=data["id"],
            name=data.get("name"),
            note=data.get("note"),
            _completed=data.get("completed"),
        )

        return {"success": True, "node": result.model_dump()}


async def test_get_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for get_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_node = WorkFlowyNode(
            id=data["id"],
            nm="Test Node",
            no="Test note",
            cp=False,
            ch=[],
            created=int(time.time()),
            modified=int(time.time()),
        )
        mock_client.get_node.return_value = mock_node

        # Call the actual function
        result = await get_node(node_id=data["id"])

        return {"success": True, "node": result.model_dump()}


async def test_list_nodes(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for list_nodes tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_nodes = [
            WorkFlowyNode(
                id=f"node-{i}",
                nm=f"Node {i}",
                cp=False,
                created=int(time.time()),
                modified=int(time.time()),
            )
            for i in range(data.get("limit", 5))
        ]
        mock_client.list_nodes.return_value = (mock_nodes, len(mock_nodes))

        # Call the actual function
        result = await list_nodes(
            parent_id=data.get("parentId"),
            _include_completed=data.get("includeCompleted", True),
            _max_depth=data.get("maxDepth"),
            limit=data.get("limit", 100),
            offset=data.get("offset", 0),
        )

        return result


async def test_delete_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for delete_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_client.delete_node.return_value = True

        # Call the actual function
        result = await delete_node(node_id=data["id"])

        return result


async def test_complete_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for complete_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_node = WorkFlowyNode(
            id=data["id"],
            nm="Completed Node",
            cp=True,
            created=int(time.time()),
            modified=int(time.time()),
        )
        mock_client.complete_node.return_value = mock_node

        # Call the actual function
        result = await complete_node(node_id=data["id"])

        return {"success": True, "node": result.model_dump()}


async def test_uncomplete_node(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for uncomplete_node tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_node = WorkFlowyNode(
            id=data["id"],
            nm="Uncompleted Node",
            cp=False,
            created=int(time.time()),
            modified=int(time.time()),
        )
        mock_client.uncomplete_node.return_value = mock_node

        # Call the actual function
        result = await uncomplete_node(node_id=data["id"])

        return {"success": True, "node": result.model_dump()}


async def test_search_nodes(data: dict[str, Any]) -> dict[str, Any]:
    """Test wrapper for search_nodes tool."""
    with patch("workflowy_mcp.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock the response
        mock_nodes = [
            WorkFlowyNode(
                id=f"search-{i}",
                nm=f"Result {i}",
                cp=False,
                created=int(time.time()),
                modified=int(time.time()),
            )
            for i in range(3)
        ]
        mock_client.search_nodes.return_value = mock_nodes

        # Call the actual function
        result = await search_nodes(
            query=data["query"], include_completed=data.get("includeCompleted", True)
        )

        return {"success": True, "nodes": result, "total": len(result)}
