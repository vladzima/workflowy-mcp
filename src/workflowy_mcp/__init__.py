"""WorkFlowy MCP Server - Model Context Protocol server for WorkFlowy API integration."""

__version__ = "0.1.0"

from .client import WorkFlowyClient
from .models import (
    APIConfiguration,
    NodeCreateRequest,
    NodeListRequest,
    NodeUpdateRequest,
    WorkFlowyNode,
)
from .server import mcp

__all__ = [
    "mcp",
    "WorkFlowyNode",
    "NodeCreateRequest",
    "NodeUpdateRequest",
    "NodeListRequest",
    "APIConfiguration",
    "WorkFlowyClient",
]
