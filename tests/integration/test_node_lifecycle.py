"""Integration tests for WorkFlowy node lifecycle operations."""

import os
import pytest
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, patch


class TestNodeLifecycle:
    """Test complete node lifecycle from creation to deletion."""

    @pytest.mark.asyncio
    async def test_full_node_lifecycle(self) -> None:
        """Test creating, updating, completing, and deleting a node."""
        from workflowy_mcp.server import create_node
        from workflowy_mcp.server import update_node
        from workflowy_mcp.server import get_node
        from workflowy_mcp.server import complete_node
        from workflowy_mcp.server import delete_node

        # Create a node
        created = await create_node.fn(
            name="Integration Test Node", note="This is a test note", priority=2
        )
        assert created["success"] is True
        node_id = created["node"]["id"]

        # Get the node to verify creation
        get_result = await get_node.fn(node_id=node_id)
        assert get_result["node"]["nm"] == "Integration Test Node"

        # Update the node
        updated = await update_node.fn(node_id=node_id, name="Updated Test Node", priority=3)
        assert updated["node"]["nm"] == "Updated Test Node"
        assert updated["node"]["priority"] == 3

        # Complete the node
        completed = await complete_node.fn(node_id=node_id)
        assert completed["node"]["cp"] is True

        # Delete the node
        deleted = await delete_node.fn(node_id=node_id)
        assert deleted["success"] is True

        # Verify deletion
        with pytest.raises(Exception):
            await get_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_parent_child_relationship(self) -> None:
        """Test creating nodes with parent-child relationships."""
        from workflowy_mcp.server import create_node
        from workflowy_mcp.server import list_nodes
        from workflowy_mcp.server import delete_node

        # Create parent node
        parent = await create_node.fn(name="Parent Node")
        parent_id = parent["node"]["id"]

        # Create child nodes
        child1 = await create_node.fn(name="Child 1", parent_id=parent_id)
        child2 = await create_node.fn(name="Child 2", parent_id=parent_id)

        # List children of parent
        children = await list_nodes.fn(parent_id=parent_id)
        assert len(children["nodes"]) == 2

        # Clean up
        await delete_node.fn(node_id=parent_id)

    @pytest.mark.asyncio
    async def test_bulk_operations(self) -> None:
        """Test performing bulk operations on multiple nodes."""
        from workflowy_mcp.server import create_node
        from workflowy_mcp.server import list_nodes
        from workflowy_mcp.server import complete_node
        from workflowy_mcp.server import delete_node

        created_ids = []

        # Create multiple nodes
        for i in range(5):
            result = await create_node.fn(name=f"Bulk Test Node {i}", priority=i % 4)
            created_ids.append(result["node"]["id"])

        # Complete all nodes
        for node_id in created_ids:
            await complete_node.fn(node_id=node_id)

        # List completed nodes
        completed = await list_nodes.fn(include_completed=True)

        # Verify all are completed
        completed_ids = [n["id"] for n in completed["nodes"]]
        for node_id in created_ids:
            assert node_id in completed_ids

        # Clean up
        for node_id in created_ids:
            await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_node_state_transitions(self) -> None:
        """Test node state transitions between completed and uncompleted."""
        from workflowy_mcp.server import create_node
        from workflowy_mcp.server import complete_node
        from workflowy_mcp.server import uncomplete_node
        from workflowy_mcp.server import get_node
        from workflowy_mcp.server import delete_node

        # Create a node
        created = await create_node.fn(name="State Test Node")
        node_id = created["node"]["id"]

        # Verify initial state (uncompleted)
        node = await get_node.fn(node_id=node_id)
        assert node["node"]["cp"] is False

        # Complete the node
        await complete_node.fn(node_id=node_id)
        node = await get_node.fn(node_id=node_id)
        assert node["node"]["cp"] is True

        # Uncomplete the node
        await uncomplete_node.fn(node_id=node_id)
        node = await get_node.fn(node_id=node_id)
        assert node["node"]["cp"] is False

        # Clean up
        await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_node_with_metadata(self) -> None:
        """Test creating and updating nodes with all metadata fields."""
        from workflowy_mcp.server import create_node
        from workflowy_mcp.server import update_node
        from workflowy_mcp.server import get_node
        from workflowy_mcp.server import delete_node

        # Create node with full metadata
        created = await create_node.fn(
            name="Metadata Test Node", note="This is a detailed note with metadata", priority=1
        )
        node_id = created["node"]["id"]

        # Update with different metadata
        updated = await update_node.fn(
            node_id=node_id, name="Updated Metadata Node", note="Updated note content", priority=3
        )

        # Verify all fields
        node = await get_node.fn(node_id=node_id)
        assert node["node"]["nm"] == "Updated Metadata Node"
        assert node["node"]["no"] == "Updated note content"
        assert node["node"]["priority"] == 3

        # Clean up
        await delete_node.fn(node_id=node_id)
