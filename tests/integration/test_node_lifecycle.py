"""Integration tests for WorkFlowy node lifecycle operations."""

import pytest


class TestNodeLifecycle:
    """Test complete node lifecycle from creation to deletion."""

    @pytest.mark.asyncio
    async def test_full_node_lifecycle(self) -> None:
        """Test creating, updating, completing, and deleting a node."""
        from workflowy_mcp.server import (
            complete_node,
            create_node,
            delete_node,
            get_node,
            update_node,
        )

        # Create a node
        created = await create_node.fn(name="Integration Test Node", note="This is a test note")
        node_id = created.id

        # Get the node to verify creation
        get_result = await get_node.fn(node_id=node_id)
        assert get_result.nm == "Integration Test Node"

        # Update the node
        updated = await update_node.fn(node_id=node_id, name="Updated Test Node")
        assert updated.nm == "Updated Test Node"

        # Complete the node
        completed = await complete_node.fn(node_id=node_id)
        assert completed.cp is True

        # Delete the node
        deleted = await delete_node.fn(node_id=node_id)
        assert deleted["success"] is True

        # Verify deletion
        from workflowy_mcp.models import NodeNotFoundError

        with pytest.raises(NodeNotFoundError):
            await get_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_parent_child_relationship(self) -> None:
        """Test creating nodes with parent-child relationships."""
        from workflowy_mcp.server import create_node, delete_node, list_nodes

        # Create parent node
        parent = await create_node.fn(name="Parent Node")
        parent_id = parent.id

        # Create child nodes
        await create_node.fn(name="Child 1", parent_id=parent_id)
        await create_node.fn(name="Child 2", parent_id=parent_id)

        # List children of parent
        children = await list_nodes.fn(parent_id=parent_id)
        assert len(children["nodes"]) == 2

        # Clean up
        await delete_node.fn(node_id=parent_id)

    @pytest.mark.asyncio
    async def test_bulk_operations(self) -> None:
        """Test performing bulk operations on multiple nodes."""
        from workflowy_mcp.server import complete_node, create_node, delete_node, list_nodes

        created_ids = []

        # Create multiple nodes
        for i in range(5):
            result = await create_node.fn(name=f"Bulk Test Node {i}")
            created_ids.append(result.id)

        # Complete all nodes
        for node_id in created_ids:
            await complete_node.fn(node_id=node_id)

        # List completed nodes
        completed = await list_nodes.fn(_include_completed=True)

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
        from workflowy_mcp.server import (
            complete_node,
            create_node,
            delete_node,
            get_node,
            uncomplete_node,
        )

        # Create a node
        created = await create_node.fn(name="State Test Node")
        node_id = created.id

        # Verify initial state (uncompleted)
        node = await get_node.fn(node_id=node_id)
        assert node.cp is False

        # Complete the node
        await complete_node.fn(node_id=node_id)
        node = await get_node.fn(node_id=node_id)
        assert node.cp is True

        # Uncomplete the node
        await uncomplete_node.fn(node_id=node_id)
        node = await get_node.fn(node_id=node_id)
        assert node.cp is False

        # Clean up
        await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_node_with_metadata(self) -> None:
        """Test creating and updating nodes with all metadata fields."""
        from workflowy_mcp.server import create_node, delete_node, get_node, update_node

        # Create node with full metadata
        created = await create_node.fn(
            name="Metadata Test Node", note="This is a detailed note with metadata"
        )
        node_id = created.id

        # Update with different metadata
        await update_node.fn(
            node_id=node_id, name="Updated Metadata Node", note="Updated note content"
        )

        # Verify all fields
        node = await get_node.fn(node_id=node_id)
        assert node.nm == "Updated Metadata Node"
        assert node.no == "Updated note content"

        # Clean up
        await delete_node.fn(node_id=node_id)
