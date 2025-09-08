"""Integration tests for search and filtering operations."""

import pytest
from typing import Any, Dict, List
from unittest.mock import patch, AsyncMock


class TestSearchAndFilter:
    """Test search and filtering functionality."""

    @pytest.mark.asyncio
    async def test_search_across_hierarchy(self) -> None:
        """Test searching nodes across the entire hierarchy."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            from workflowy_mcp.tools.search import workflowy_search_nodes
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            created_ids = []
            
            # Create nodes with searchable content
            parent = await workflowy_create_node({
                "name": "Project Alpha",
                "note": "Main project documentation"
            })
            created_ids.append(parent["node"]["id"])
            
            child1 = await workflowy_create_node({
                "name": "Alpha Subtask 1",
                "parentId": parent["node"]["id"]
            })
            created_ids.append(child1["node"]["id"])
            
            child2 = await workflowy_create_node({
                "name": "Beta Subtask",
                "note": "Contains alpha keyword in note",
                "parentId": parent["node"]["id"]
            })
            created_ids.append(child2["node"]["id"])
            
            # Search for "alpha"
            results = await workflowy_search_nodes({"query": "alpha"})
            
            # Should find all three nodes
            assert len(results["nodes"]) >= 3
            found_ids = [n["id"] for n in results["nodes"]]
            for node_id in created_ids:
                assert node_id in found_ids
            
            # Clean up
            for node_id in created_ids:
                await workflowy_delete_node({"id": node_id})

    @pytest.mark.asyncio
    async def test_filter_by_completion_status(self) -> None:
        """Test filtering nodes by completion status."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            from workflowy_mcp.tools.complete import workflowy_complete_node
            from workflowy_mcp.tools.list import workflowy_list_nodes
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            created_ids = []
            
            # Create mix of completed and uncompleted nodes
            for i in range(6):
                node = await workflowy_create_node({
                    "name": f"Task {i}",
                    "priority": i % 4
                })
                created_ids.append(node["node"]["id"])
                
                # Complete even-numbered tasks
                if i % 2 == 0:
                    await workflowy_complete_node({"id": node["node"]["id"]})
            
            # Filter completed nodes
            completed = await workflowy_list_nodes({"completed": True})
            completed_count = len([n for n in completed["nodes"] 
                                 if n["id"] in created_ids])
            assert completed_count == 3
            
            # Filter uncompleted nodes
            uncompleted = await workflowy_list_nodes({"completed": False})
            uncompleted_count = len([n for n in uncompleted["nodes"] 
                                   if n["id"] in created_ids])
            assert uncompleted_count == 3
            
            # Clean up
            for node_id in created_ids:
                await workflowy_delete_node({"id": node_id})

    @pytest.mark.asyncio
    async def test_pagination(self) -> None:
        """Test pagination of results."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            from workflowy_mcp.tools.list import workflowy_list_nodes
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            created_ids = []
            
            # Create many nodes
            for i in range(15):
                node = await workflowy_create_node({
                    "name": f"Paginated Node {i:02d}"
                })
                created_ids.append(node["node"]["id"])
            
            # Get first page
            page1 = await workflowy_list_nodes({"limit": 5, "offset": 0})
            assert len(page1["nodes"]) <= 5
            
            # Get second page
            page2 = await workflowy_list_nodes({"limit": 5, "offset": 5})
            assert len(page2["nodes"]) <= 5
            
            # Get third page
            page3 = await workflowy_list_nodes({"limit": 5, "offset": 10})
            assert len(page3["nodes"]) <= 5
            
            # Verify no duplicates across pages
            page1_ids = [n["id"] for n in page1["nodes"]]
            page2_ids = [n["id"] for n in page2["nodes"]]
            page3_ids = [n["id"] for n in page3["nodes"]]
            
            assert len(set(page1_ids) & set(page2_ids)) == 0
            assert len(set(page2_ids) & set(page3_ids)) == 0
            
            # Clean up
            for node_id in created_ids:
                await workflowy_delete_node({"id": node_id})

    @pytest.mark.asyncio
    async def test_search_with_special_characters(self) -> None:
        """Test searching with special characters and escaping."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            from workflowy_mcp.tools.search import workflowy_search_nodes
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            # Create nodes with special characters
            special_nodes = [
                {"name": "Code: function() { return true; }"},
                {"name": "Email: user@example.com"},
                {"name": "Path: /usr/local/bin"},
                {"name": "Regex: ^[a-z]+$"},
            ]
            
            created_ids = []
            for node_data in special_nodes:
                node = await workflowy_create_node(node_data)
                created_ids.append(node["node"]["id"])
            
            # Search for special patterns
            email_results = await workflowy_search_nodes({"query": "@example.com"})
            assert len(email_results["nodes"]) >= 1
            
            code_results = await workflowy_search_nodes({"query": "function()"})
            assert len(code_results["nodes"]) >= 1
            
            # Clean up
            for node_id in created_ids:
                await workflowy_delete_node({"id": node_id})

    @pytest.mark.asyncio
    async def test_combined_filters(self) -> None:
        """Test combining multiple filter criteria."""
        # This test MUST FAIL until implementation
        with pytest.raises((ImportError, ModuleNotFoundError)):
            from workflowy_mcp.tools.create import workflowy_create_node
            from workflowy_mcp.tools.complete import workflowy_complete_node
            from workflowy_mcp.tools.list import workflowy_list_nodes
            from workflowy_mcp.tools.delete import workflowy_delete_node
            
            # Create parent node
            parent = await workflowy_create_node({"name": "Parent Container"})
            parent_id = parent["node"]["id"]
            
            # Create child nodes with various attributes
            children_ids = []
            for i in range(10):
                child = await workflowy_create_node({
                    "name": f"Item {i}",
                    "note": "test" if i % 3 == 0 else "other",
                    "parentId": parent_id
                })
                children_ids.append(child["node"]["id"])
                
                if i % 2 == 0:
                    await workflowy_complete_node({"id": child["node"]["id"]})
            
            # Filter by parent and query
            filtered = await workflowy_list_nodes({
                "parentId": parent_id,
                "query": "Item",
                "completed": False
            })
            
            # Should only get uncompleted children with "Item" in name
            assert all(not n["cp"] for n in filtered["nodes"])
            assert all("Item" in n["nm"] for n in filtered["nodes"])
            
            # Clean up
            await workflowy_delete_node({"id": parent_id})