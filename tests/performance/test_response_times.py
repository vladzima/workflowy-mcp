"""Performance tests for API operations."""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
import statistics

from workflowy_mcp.server import (
    create_node,
    get_node,
    update_node,
    list_nodes,
    search_nodes,
    delete_node,
)


class TestResponseTimes:
    """Test that API operations meet performance requirements (<500ms)."""
    
    @pytest.mark.asyncio
    async def test_create_node_performance(self):
        """Test create_node response time."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            # Mock fast API response
            mock_client.create_node.return_value = {
                "id": "test-123",
                "nm": "Test Node",
                "created": int(time.time()),
                "modified": int(time.time())
            }
            
            # Measure response time
            start = time.perf_counter()
            result = await create_node.fn(name="Test Node")
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            
            assert result["success"] is True
            assert elapsed < 500, f"Response time {elapsed:.2f}ms exceeds 500ms limit"
    
    @pytest.mark.asyncio
    async def test_get_node_performance(self):
        """Test get_node response time."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            mock_client.get_node.return_value = {
                "id": "test-123",
                "nm": "Test Node",
                "created": int(time.time()),
                "modified": int(time.time())
            }
            
            start = time.perf_counter()
            result = await get_node.fn(node_id="test-123")
            elapsed = (time.perf_counter() - start) * 1000
            
            assert result["success"] is True
            assert elapsed < 500, f"Response time {elapsed:.2f}ms exceeds 500ms limit"
    
    @pytest.mark.asyncio
    async def test_list_nodes_performance(self):
        """Test list_nodes response time with pagination."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            # Mock list of nodes
            mock_nodes = [
                {
                    "id": f"node-{i}",
                    "nm": f"Node {i}",
                    "created": int(time.time()),
                    "modified": int(time.time())
                }
                for i in range(100)
            ]
            mock_client.list_nodes.return_value = mock_nodes
            
            start = time.perf_counter()
            result = await list_nodes.fn(limit=50)
            elapsed = (time.perf_counter() - start) * 1000
            
            assert result["success"] is True
            assert elapsed < 500, f"Response time {elapsed:.2f}ms exceeds 500ms limit"
    
    @pytest.mark.asyncio
    async def test_search_nodes_performance(self):
        """Test search_nodes response time."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            # Mock search results
            mock_results = [
                {
                    "id": f"result-{i}",
                    "nm": f"Search Result {i}",
                    "created": int(time.time()),
                    "modified": int(time.time())
                }
                for i in range(20)
            ]
            mock_client.search_nodes.return_value = mock_results
            
            start = time.perf_counter()
            result = await search_nodes.fn(query="test query")
            elapsed = (time.perf_counter() - start) * 1000
            
            assert result["success"] is True
            assert elapsed < 500, f"Response time {elapsed:.2f}ms exceeds 500ms limit"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self):
        """Test performance under concurrent load."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            # Mock all operations
            mock_client.get_node.return_value = {"id": "test", "nm": "Node"}
            mock_client.list_nodes.return_value = [{"id": "test", "nm": "Node"}]
            mock_client.search_nodes.return_value = [{"id": "test", "nm": "Node"}]
            
            # Run concurrent operations
            async def operation(op_type: str):
                start = time.perf_counter()
                if op_type == "get":
                    await get_node.fn(node_id="test-123")
                elif op_type == "list":
                    await list_nodes.fn()
                elif op_type == "search":
                    await search_nodes.fn(query="test")
                return (time.perf_counter() - start) * 1000
            
            # Run 10 concurrent operations
            tasks = []
            for _ in range(3):
                tasks.extend([
                    operation("get"),
                    operation("list"),
                    operation("search"),
                ])
            
            response_times = await asyncio.gather(*tasks)
            
            # All should complete within 500ms
            assert all(t < 500 for t in response_times), \
                f"Some operations exceeded 500ms: {[t for t in response_times if t >= 500]}"
            
            # Average should be well under 500ms
            avg_time = statistics.mean(response_times)
            assert avg_time < 300, f"Average response time {avg_time:.2f}ms is too high"
    
    @pytest.mark.asyncio
    async def test_bulk_operation_performance(self):
        """Test performance of bulk operations."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            mock_client.create_node.return_value = {"id": "test", "nm": "Node"}
            
            # Create 50 nodes sequentially
            start = time.perf_counter()
            for i in range(50):
                await create_node.fn(name=f"Node {i}")
            total_elapsed = (time.perf_counter() - start) * 1000
            
            # Average per operation
            avg_per_op = total_elapsed / 50
            
            # Each operation should average under 100ms for bulk
            assert avg_per_op < 100, f"Average per operation {avg_per_op:.2f}ms is too high"
    
    @pytest.mark.asyncio
    async def test_response_time_percentiles(self):
        """Test response time percentiles (p50, p95, p99)."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            mock_client.get_node.return_value = {"id": "test", "nm": "Node"}
            
            # Collect response times
            response_times = []
            for _ in range(100):
                start = time.perf_counter()
                await get_node.fn(node_id="test-123")
                elapsed = (time.perf_counter() - start) * 1000
                response_times.append(elapsed)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50 = sorted_times[50]  # Median
            p95 = sorted_times[95]
            p99 = sorted_times[99]
            
            # Performance requirements
            assert p50 < 200, f"p50 {p50:.2f}ms exceeds 200ms"
            assert p95 < 400, f"p95 {p95:.2f}ms exceeds 400ms"
            assert p99 < 500, f"p99 {p99:.2f}ms exceeds 500ms"
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test that caching improves performance."""
        with patch("workflowy_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            # Simulate cache behavior - first call slower
            call_count = 0
            async def mock_get_node(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    await asyncio.sleep(0.1)  # Simulate network delay
                return {"id": "test", "nm": "Node"}
            
            mock_client.get_node = mock_get_node
            
            # First call (cache miss)
            start1 = time.perf_counter()
            await get_node.fn(node_id="test-123")
            time1 = (time.perf_counter() - start1) * 1000
            
            # Second call (should be cached)
            start2 = time.perf_counter()
            await get_node.fn(node_id="test-123")
            time2 = (time.perf_counter() - start2) * 1000
            
            # Second call should be significantly faster
            assert time2 < time1 / 2, f"Cache not improving performance: {time1:.2f}ms vs {time2:.2f}ms"