"""Shared test fixtures and configuration for WorkFlowy MCP tests."""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastmcp import FastMCP

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set up test environment
os.environ.setdefault("WORKFLOWY_API_KEY", "test-api-key")
os.environ.setdefault("WORKFLOWY_API_URL", "https://api.test.workflowy.com")
os.environ.setdefault("LOG_LEVEL", "ERROR")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_mcp_server() -> AsyncGenerator[FastMCP, None]:
    """Create a mock MCP server for testing."""
    server = FastMCP("workflowy-test")
    yield server


@pytest.fixture
def mock_api_client() -> AsyncMock:
    """Create a mock WorkFlowy API client."""
    client = AsyncMock()
    client.base_url = "https://api.workflowy.com"
    client.api_key = "test-api-key"
    return client


@pytest.fixture
def sample_node_data() -> dict[str, Any]:
    """Provide sample WorkFlowy node data."""
    return {
        "id": "node-123",
        "nm": "Sample Node",
        "no": "This is a note",
        "cp": False,
        "created": 1704067200,
        "modified": 1704067200,
        "priority": 1,
    }


@pytest.fixture
def sample_create_request() -> dict[str, Any]:
    """Provide sample create node request data."""
    return {
        "name": "New Test Node",
        "note": "Test note content",
        "parentId": None,
        "priority": 2,
    }


@pytest.fixture
def sample_update_request() -> dict[str, Any]:
    """Provide sample update node request data."""
    return {
        "id": "node-123",
        "name": "Updated Node Name",
        "note": "Updated note content",
        "priority": 3,
    }


@pytest.fixture
def sample_list_request() -> dict[str, Any]:
    """Provide sample list nodes request data."""
    return {
        "parentId": None,
        "completed": False,
        "query": "test",
        "limit": 100,
        "offset": 0,
    }


@pytest.fixture
def mock_tool_context() -> MagicMock:
    """Create a mock MCP tool context."""
    context = MagicMock()
    context.logger = MagicMock()
    return context
