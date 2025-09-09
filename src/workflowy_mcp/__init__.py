"""WorkFlowy MCP Server - Model Context Protocol server for WorkFlowy API integration."""

__version__ = "0.1.0"

from .server import mcp
from .models import (
    WorkFlowyNode,
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeListRequest,
    APIConfiguration,
)
from .client import WorkFlowyClient

__all__ = [
    "mcp",
    "WorkFlowyNode",
    "NodeCreateRequest",
    "NodeUpdateRequest",
    "NodeListRequest",
    "APIConfiguration",
    "WorkFlowyClient",
]
