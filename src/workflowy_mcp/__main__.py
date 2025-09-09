"""Main entry point for WorkFlowy MCP Server."""

import asyncio
import sys
from workflowy_mcp.server import mcp


def main():
    """Run the MCP server."""
    asyncio.run(mcp.run())


if __name__ == "__main__":
    main()