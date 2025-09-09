"""Test utilities for WorkFlowy MCP tests."""

import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set up test environment variables if not already set
if "WORKFLOWY_API_KEY" not in os.environ:
    os.environ["WORKFLOWY_API_KEY"] = "test-api-key"

def setup_test_env():
    """Set up test environment."""
    os.environ.setdefault("WORKFLOWY_API_KEY", "test-api-key")
    os.environ.setdefault("WORKFLOWY_API_URL", "https://api.test.workflowy.com")
    os.environ.setdefault("LOG_LEVEL", "ERROR")  # Reduce noise in tests