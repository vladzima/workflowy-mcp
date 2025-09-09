"""Main entry point for WorkFlowy MCP Server."""

import asyncio

from workflowy_mcp.server import mcp


def main() -> None:
    """Run the MCP server."""
    asyncio.run(mcp.run())  # type: ignore[func-returns-value]


if __name__ == "__main__":
    main()
