"""Integration tests for search and filtering operations."""

import pytest


class TestSearchAndFilter:
    """Test search and filtering functionality."""

    @pytest.mark.asyncio
    async def test_search_across_hierarchy(self) -> None:
        """Test searching nodes across the entire hierarchy."""
        from workflowy_mcp.server import create_node, delete_node, search_nodes

        created_ids = []

        # Create nodes with searchable content
        parent = await create_node.fn(name="Project Alpha", note="Main project documentation")
        created_ids.append(parent.id)

        child1 = await create_node.fn(name="Alpha Subtask 1", parent_id=parent.id)
        created_ids.append(child1.id)

        child2 = await create_node.fn(
            name="Beta Subtask",
            note="Contains alpha keyword in note",
            parent_id=parent.id,
        )
        created_ids.append(child2.id)

        # Search for "alpha"
        results = await search_nodes.fn(query="alpha")

        # Should find all three nodes
        assert len(results) >= 3
        found_ids = [n["id"] for n in results]
        for node_id in created_ids:
            assert node_id in found_ids

        # Clean up
        for node_id in created_ids:
            await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="_include_completed parameter not implemented in server")
    async def test_filter_by_completion_status(self) -> None:
        """Test filtering nodes by completion status."""
        from workflowy_mcp.server import complete_node, create_node, delete_node, list_nodes

        created_ids = []

        # Create mix of completed and uncompleted nodes
        uncompleted1 = await create_node.fn(name="Active Task 1")
        created_ids.append(uncompleted1.id)

        uncompleted2 = await create_node.fn(name="Active Task 2")
        created_ids.append(uncompleted2.id)

        completed1 = await create_node.fn(name="Done Task 1")
        created_ids.append(completed1.id)
        await complete_node.fn(node_id=completed1.id)

        completed2 = await create_node.fn(name="Done Task 2")
        created_ids.append(completed2.id)
        await complete_node.fn(node_id=completed2.id)

        # List only uncompleted nodes
        uncompleted = await list_nodes.fn(_include_completed=False)
        uncompleted_ids = [n["id"] for n in uncompleted["nodes"]]

        assert uncompleted1.id in uncompleted_ids
        assert uncompleted2.id in uncompleted_ids
        assert completed1.id not in uncompleted_ids
        assert completed2.id not in uncompleted_ids

        # List including completed nodes
        all_nodes = await list_nodes.fn(_include_completed=True)
        all_ids = [n["id"] for n in all_nodes["nodes"]]

        for node_id in created_ids:
            assert node_id in all_ids

        # Clean up
        for node_id in created_ids:
            await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    async def test_search_with_special_characters(self) -> None:
        """Test searching with special characters and escaping."""
        from workflowy_mcp.server import create_node, delete_node, search_nodes

        # Create nodes with special characters
        node1 = await create_node.fn(name="Code: function()", note="Implementation of foo()")

        node2 = await create_node.fn(name="Email@example.com", note="Contact information")

        node3 = await create_node.fn(name="Price: $99.99", note="Product pricing")

        # Search for special character content
        results1 = await search_nodes.fn(query="function()")
        assert len(results1) >= 1

        results2 = await search_nodes.fn(query="@example")
        assert len(results2) >= 1

        results3 = await search_nodes.fn(query="$99")
        assert len(results3) >= 1

        # Clean up
        await delete_node.fn(node_id=node1.id)
        await delete_node.fn(node_id=node2.id)
        await delete_node.fn(node_id=node3.id)

    @pytest.mark.asyncio
    async def test_list_with_pagination(self) -> None:
        """Test listing nodes with limit and offset pagination."""
        from workflowy_mcp.server import create_node, delete_node, list_nodes

        created_ids = []

        # Create multiple nodes for pagination
        for i in range(10):
            result = await create_node.fn(name=f"Page Test Node {i:02d}")
            created_ids.append(result.id)

        # Get first page
        page1 = await list_nodes.fn(limit=5, offset=0)
        assert len(page1["nodes"]) == 5

        # Get second page
        page2 = await list_nodes.fn(limit=5, offset=5)
        assert len(page2["nodes"]) == 5

        # Ensure no overlap between pages
        page1_ids = [n["id"] for n in page1["nodes"]]
        page2_ids = [n["id"] for n in page2["nodes"]]
        assert len(set(page1_ids) & set(page2_ids)) == 0

        # Clean up
        for node_id in created_ids:
            await delete_node.fn(node_id=node_id)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="_max_depth parameter not implemented in server")
    async def test_list_with_depth_limit(self) -> None:
        """Test listing nodes with max depth limitation."""
        from workflowy_mcp.server import create_node, delete_node, list_nodes

        # Create nested hierarchy
        root = await create_node.fn(name="Root")
        root_id = root.id

        level1 = await create_node.fn(name="Level 1", parent_id=root_id)

        level2 = await create_node.fn(name="Level 2", parent_id=level1.id)

        await create_node.fn(name="Level 3", parent_id=level2.id)

        # List with depth=1 (only direct children)
        shallow = await list_nodes.fn(parent_id=root_id, _max_depth=1)
        shallow_names = [n["nm"] for n in shallow["nodes"]]

        assert "Level 1" in shallow_names
        assert "Level 2" not in shallow_names
        assert "Level 3" not in shallow_names

        # List with depth=2
        deeper = await list_nodes.fn(parent_id=root_id, _max_depth=2)
        deeper_names = [n["nm"] for n in deeper["nodes"]]

        assert "Level 1" in deeper_names
        assert "Level 2" in deeper_names
        assert "Level 3" not in deeper_names

        # Clean up
        await delete_node.fn(node_id=root_id)

    @pytest.mark.asyncio
    async def test_search_case_sensitivity(self) -> None:
        """Test that search is case-insensitive."""
        from workflowy_mcp.server import create_node, delete_node, search_nodes

        # Create nodes with mixed case
        node1 = await create_node.fn(name="UPPERCASE PROJECT")
        node2 = await create_node.fn(name="lowercase project")
        node3 = await create_node.fn(name="MiXeD CaSe PrOjEcT")

        # Search with different cases
        results_upper = await search_nodes.fn(query="PROJECT")
        results_lower = await search_nodes.fn(query="project")
        results_mixed = await search_nodes.fn(query="PrOjEcT")

        # All searches should return same number of results
        assert len(results_upper) == len(results_lower)
        assert len(results_upper) == len(results_mixed)
        assert len(results_upper) >= 3

        # Clean up
        await delete_node.fn(node_id=node1.id)
        await delete_node.fn(node_id=node2.id)
        await delete_node.fn(node_id=node3.id)

    @pytest.mark.asyncio
    async def test_empty_search_results(self) -> None:
        """Test handling of searches that return no results."""
        from workflowy_mcp.server import search_nodes

        # Search for something that shouldn't exist
        results = await search_nodes.fn(query="xyzabc123nonexistent99999")

        assert results == []
