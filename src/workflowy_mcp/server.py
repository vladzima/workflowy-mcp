"""WorkFlowy MCP server implementation using FastMCP."""

import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastmcp import FastMCP

from .client import AdaptiveRateLimiter, WorkFlowyClient
from .config import ServerConfig, setup_logging
from .models import (
    NodeCreateRequest,
    NodeListRequest,
    NodeUpdateRequest,
    WorkFlowyNode,
)

logger = logging.getLogger(__name__)

# Global client instance
_client: WorkFlowyClient | None = None
_rate_limiter: AdaptiveRateLimiter | None = None


def get_client() -> WorkFlowyClient:
    """Get the global WorkFlowy client instance."""
    global _client
    if _client is None:
        raise RuntimeError("WorkFlowy client not initialized. Server not started properly.")
    return _client


@asynccontextmanager
async def lifespan(_app: FastMCP):  # type: ignore[no-untyped-def]
    """Manage server lifecycle."""
    global _client, _rate_limiter

    # Setup
    logger.info("Starting WorkFlowy MCP server")

    # Load configuration
    config = ServerConfig()  # type: ignore[call-arg]
    api_config = config.get_api_config()

    # Initialize rate limiter (default 10 req/s)
    _rate_limiter = AdaptiveRateLimiter(
        initial_rate=10.0,
        min_rate=1.0,
        max_rate=100.0,
    )

    # Initialize client
    _client = WorkFlowyClient(api_config)

    logger.info(f"WorkFlowy client initialized with base URL: {api_config.base_url}")

    yield

    # Cleanup
    logger.info("Shutting down WorkFlowy MCP server")
    if _client:
        await _client.close()
        _client = None
    _rate_limiter = None


# Initialize FastMCP server
mcp = FastMCP(
    "WorkFlowy MCP Server",
    version="0.1.0",
    instructions="MCP server for managing WorkFlowy outlines and nodes",
    lifespan=lifespan,
)


# Tool: Create Node
@mcp.tool(name="workflowy_create_node", description="Create a new node in WorkFlowy")
async def create_node(
    name: str,
    parent_id: str | None = None,
    note: str | None = None,
    layout_mode: Literal["bullets", "todo", "h1", "h2", "h3"] | None = None,
    position: Literal["top", "bottom"] = "top",
    _completed: bool = False,
) -> WorkFlowyNode:
    """Create a new node in WorkFlowy.

    Args:
        name: The text content of the node
        parent_id: ID of the parent node (optional)
        note: Additional note/description for the node
        layout_mode: Layout mode for the node (bullets, todo, h1, h2, h3) (optional)
        position: Where to place the new node - "top" (default) or "bottom"
        _completed: Whether the node should be marked as completed (not used)

    Returns:
        The created WorkFlowy node
    """
    client = get_client()

    request = NodeCreateRequest(  # type: ignore[call-arg]
        name=name,
        parent_id=parent_id,
        note=note,
        layoutMode=layout_mode,
        position=position,
    )

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        node = await client.create_node(request)
        if _rate_limiter:
            _rate_limiter.on_success()
        return node
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Update Node
@mcp.tool(name="workflowy_update_node", description="Update an existing WorkFlowy node")
async def update_node(
    node_id: str,
    name: str | None = None,
    note: str | None = None,
    layout_mode: Literal["bullets", "todo", "h1", "h2", "h3"] | None = None,
    _completed: bool | None = None,
) -> WorkFlowyNode:
    """Update an existing WorkFlowy node.

    Args:
        node_id: The ID of the node to update
        name: New text content for the node (optional)
        note: New note/description (optional)
        layout_mode: New layout mode for the node (bullets, todo, h1, h2, h3) (optional)
        _completed: New completion status (not used - use complete_node/uncomplete_node)

    Returns:
        The updated WorkFlowy node
    """
    client = get_client()

    request = NodeUpdateRequest(  # type: ignore[call-arg]
        name=name,
        note=note,
        layoutMode=layout_mode,
    )

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        node = await client.update_node(node_id, request)
        if _rate_limiter:
            _rate_limiter.on_success()
        return node
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Get Node
@mcp.tool(name="workflowy_get_node", description="Retrieve a specific WorkFlowy node by ID")
async def get_node(node_id: str) -> WorkFlowyNode:
    """Retrieve a specific WorkFlowy node.

    Args:
        node_id: The ID of the node to retrieve

    Returns:
        The requested WorkFlowy node
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        node = await client.get_node(node_id)
        if _rate_limiter:
            _rate_limiter.on_success()
        return node
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: List Nodes
@mcp.tool(name="workflowy_list_nodes", description="List WorkFlowy nodes with optional filtering")
async def list_nodes(
    parent_id: str | None = None,
    _include_completed: bool = True,
    _max_depth: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """List WorkFlowy nodes with optional filtering.

    Args:
        parent_id: Filter by parent node ID (optional)
        _include_completed: Whether to include completed nodes (not used)
        _max_depth: Maximum depth of child nodes to retrieve (not used)
        limit: Maximum number of nodes to return
        offset: Number of nodes to skip (for pagination)

    Returns:
        Dictionary with 'nodes' list and 'total' count
    """
    client = get_client()

    request = NodeListRequest(  # type: ignore[call-arg]
        parentId=parent_id,
        limit=limit,
        offset=offset,
    )

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        nodes, total = await client.list_nodes(request)
        if _rate_limiter:
            _rate_limiter.on_success()
        return {
            "nodes": [node.model_dump() for node in nodes],
            "total": total,
        }
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Delete Node
@mcp.tool(name="workflowy_delete_node", description="Delete a WorkFlowy node and all its children")
async def delete_node(node_id: str) -> dict:
    """Delete a WorkFlowy node and all its children.

    Args:
        node_id: The ID of the node to delete

    Returns:
        Dictionary with success status
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        success = await client.delete_node(node_id)
        if _rate_limiter:
            _rate_limiter.on_success()
        return {"success": success, "deleted_id": node_id}
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Complete Node
@mcp.tool(name="workflowy_complete_node", description="Mark a WorkFlowy node as completed")
async def complete_node(node_id: str) -> WorkFlowyNode:
    """Mark a WorkFlowy node as completed.

    Args:
        node_id: The ID of the node to complete

    Returns:
        The updated WorkFlowy node
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        node = await client.complete_node(node_id)
        if _rate_limiter:
            _rate_limiter.on_success()
        return node
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Uncomplete Node
@mcp.tool(name="workflowy_uncomplete_node", description="Mark a WorkFlowy node as not completed")
async def uncomplete_node(node_id: str) -> WorkFlowyNode:
    """Mark a WorkFlowy node as not completed.

    Args:
        node_id: The ID of the node to uncomplete

    Returns:
        The updated WorkFlowy node
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        node = await client.uncomplete_node(node_id)
        if _rate_limiter:
            _rate_limiter.on_success()
        return node
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Tool: Search Nodes
@mcp.tool(name="workflowy_search_nodes", description="Search for WorkFlowy nodes by text content")
async def search_nodes(
    query: str,
    include_completed: bool = True,
) -> list:
    """Search for WorkFlowy nodes by text content.

    Args:
        query: The search query string
        include_completed: Whether to include completed nodes in results

    Returns:
        List of matching WorkFlowy nodes
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        nodes = await client.search_nodes(query, include_completed)
        if _rate_limiter:
            _rate_limiter.on_success()
        return [node.model_dump() for node in nodes]
    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


# Resource: WorkFlowy Outline
@mcp.resource(
    uri="workflowy://outline",
    name="workflowy_outline",
    description="The complete WorkFlowy outline structure",
)
async def get_outline() -> str:
    """Get the complete WorkFlowy outline as a formatted string.

    Returns:
        Formatted string representation of the outline
    """
    client = get_client()

    if _rate_limiter:
        await _rate_limiter.acquire()

    try:
        # Get root nodes
        request = NodeListRequest(  # type: ignore[call-arg]
            limit=1000,  # Get many nodes
        )
        nodes, _ = await client.list_nodes(request)

        if _rate_limiter:
            _rate_limiter.on_success()

        # Format outline
        def format_node(node: WorkFlowyNode, indent: int = 0) -> str:
            lines = []
            prefix = "  " * indent + "- "
            status = "[x] " if node.cp else ""
            lines.append(f"{prefix}{status}{node.nm or '(untitled)'}")

            if node.no:
                note_prefix = "  " * (indent + 1)
                lines.append(f"{note_prefix}Note: {node.no}")

            if node.ch:
                for child in node.ch:
                    lines.append(format_node(child, indent + 1))

            return "\n".join(lines)

        outline_parts = [format_node(node) for node in nodes]
        return "\n".join(outline_parts)

    except Exception as e:
        if _rate_limiter and hasattr(e, "__class__") and e.__class__.__name__ == "RateLimitError":
            _rate_limiter.on_rate_limit(getattr(e, "retry_after", None))
        raise


if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Run the server

    mcp.run(transport="stdio")
