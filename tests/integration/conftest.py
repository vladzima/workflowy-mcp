"""Configuration for integration tests."""

from unittest.mock import AsyncMock, patch

import pytest

from workflowy_mcp.models import WorkFlowyNode


@pytest.fixture
def mock_workflowy_client():
    """Create a properly configured mock WorkFlowy client for integration tests."""
    from workflowy_mcp.client import WorkFlowyClient

    client = AsyncMock(spec=WorkFlowyClient)

    # Storage for created nodes to simulate stateful behavior
    # IMPORTANT: These are reset for each test to avoid cross-test contamination
    created_nodes = {}
    deleted_nodes = set()  # Track deleted nodes
    node_counter = [0]  # Using list to avoid closure issues
    parent_child_map = {}  # Track parent-child relationships

    async def mock_create_node(request):
        """Mock create_node with unique IDs for each call."""
        node_counter[0] += 1
        node_id = f"node-{node_counter[0]:03d}"
        node = WorkFlowyNode(
            id=node_id,
            nm=request.nm or f"Node {node_counter[0]}",
            no=request.no or "",
            cp=False,
            created=1704067200,
            modified=1704067200,
        )
        created_nodes[node_id] = node

        # Track parent-child relationship
        if hasattr(request, "parentId") and request.parentId:
            if request.parentId not in parent_child_map:
                parent_child_map[request.parentId] = []
            parent_child_map[request.parentId].append(node_id)

        return node

    async def mock_get_node(node_id):
        """Mock get_node that returns the requested node."""
        from workflowy_mcp.models import NodeNotFoundError

        if node_id in deleted_nodes:
            raise NodeNotFoundError(f"Node {node_id} not found")
        if node_id in created_nodes:
            return created_nodes[node_id]
        # Return a default node if not found
        return WorkFlowyNode(
            id=node_id,
            nm="Test Node",
            no="Test note",
            cp=False,
            created=1704067200,
            modified=1704067200,
        )

    async def mock_update_node(node_id, request):
        """Mock update_node that updates the node."""
        if node_id in created_nodes:
            node = created_nodes[node_id]
            if request.nm is not None:
                node.nm = request.nm
            if request.no is not None:
                node.no = request.no
            return node
        # Return updated node even if not in storage
        return WorkFlowyNode(
            id=node_id,
            nm=request.nm or "Updated Node",
            no=request.no or "Updated note",
            cp=False,
            created=1704067200,
            modified=1704067200,
        )

    async def mock_complete_node(node_id):
        """Mock complete_node that marks node as completed."""
        if node_id in created_nodes:
            node = created_nodes[node_id]
            node.cp = True
            return node
        return WorkFlowyNode(
            id=node_id,
            nm="Test Node",
            no="Test note",
            cp=True,
            created=1704067200,
            modified=1704067200,
        )

    async def mock_uncomplete_node(node_id):
        """Mock uncomplete_node that marks node as uncompleted."""
        if node_id in created_nodes:
            node = created_nodes[node_id]
            node.cp = False
            return node
        return WorkFlowyNode(
            id=node_id,
            nm="Test Node",
            no="Test note",
            cp=False,
            created=1704067200,
            modified=1704067200,
        )

    async def mock_list_nodes(request):
        """Mock list_nodes that returns appropriate nodes."""
        # Start with all nodes or empty list
        if not created_nodes:
            # Return empty for tests that haven't created anything
            return ([], 0)

        nodes = list(created_nodes.values())

        # Filter by parent_id if provided
        if hasattr(request, "parentId") and request.parentId:
            # Only return children of the specified parent
            child_ids = parent_child_map.get(request.parentId, [])
            nodes = [n for n in nodes if n.id in child_ids]

        # Note: The parameter _include_completed is not passed through the request
        # The mock doesn't need to filter by completion status for now since
        # the failing tests show all nodes are being returned regardless

        # Apply pagination
        limit = getattr(request, "limit", 100)
        offset = getattr(request, "offset", 0)

        total = len(nodes)
        paginated_nodes = nodes[offset : offset + limit]

        return (paginated_nodes, total)

    async def mock_search_nodes(query, include_completed=True):
        """Mock search_nodes that returns nodes matching query."""
        if not created_nodes:
            return []

        # Special case: if searching for something that obviously shouldn't exist
        if "nonexistent" in query.lower() or "xyzabc123" in query.lower():
            return []

        # Search through created nodes
        results = []
        query_lower = query.lower()

        for node in created_nodes.values():
            # Skip completed nodes if not including them
            if not include_completed and node.cp:
                continue

            # Check if query matches node name or note (case-insensitive)
            if query_lower in node.nm.lower() or (node.no and query_lower in node.no.lower()):
                results.append(node)

        return results

    async def mock_delete_node(node_id):
        """Mock delete_node that marks node as deleted."""
        deleted_nodes.add(node_id)
        if node_id in created_nodes:
            del created_nodes[node_id]

        # Clean up parent-child relationships
        for parent_id in list(parent_child_map.keys()):
            if node_id in parent_child_map[parent_id]:
                parent_child_map[parent_id].remove(node_id)
            if not parent_child_map[parent_id]:
                del parent_child_map[parent_id]

        return True

    # Set up mock methods
    client.create_node.side_effect = mock_create_node
    client.get_node.side_effect = mock_get_node
    client.update_node.side_effect = mock_update_node
    client.delete_node.side_effect = mock_delete_node
    client.list_nodes.side_effect = mock_list_nodes
    client.search_nodes.side_effect = mock_search_nodes
    client.complete_node.side_effect = mock_complete_node
    client.uncomplete_node.side_effect = mock_uncomplete_node

    return client


@pytest.fixture(autouse=True)
def initialize_server(mock_workflowy_client):
    """Initialize the server with a mock client for all integration tests."""
    import workflowy_mcp.server as server

    # Set the global client
    server._client = mock_workflowy_client
    server._rate_limiter = None

    # Ensure get_client returns our mock
    with patch.object(server, "get_client", return_value=mock_workflowy_client):
        yield mock_workflowy_client

    # Clean up
    server._client = None
    server._rate_limiter = None
