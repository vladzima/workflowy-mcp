#!/bin/bash
# WorkFlowy MCP Server Installation Script

set -e  # Exit on error

echo "================================================"
echo "WorkFlowy MCP Server Installation"
echo "================================================"
echo ""

# Check for Python 3.10+
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed but Python 3.10+ is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION is installed"
echo ""

# Check for pip
echo "Checking pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
fi
echo "✅ pip is installed"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✅ pip upgraded"
echo ""

# Install package from PyPI
echo "Installing WorkFlowy MCP Server..."
pip install workflowy-mcp
echo "✅ WorkFlowy MCP Server installed"
echo ""

# Note: API key will be configured in Claude Desktop config
echo "✅ Package installation complete"
echo ""

# Create MCP configuration for Claude Desktop
echo "Setting up MCP configuration for Claude Desktop..."
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "ℹ️  Claude Desktop configuration already exists"
    echo "   To add WorkFlowy MCP Server, edit: $CLAUDE_CONFIG_FILE"
    echo ""
    echo "   Add this to the 'mcpServers' section:"
    echo ""
    cat << EOF
    "workflowy": {
      "command": "$(pwd)/venv/bin/python",
      "args": ["-m", "workflowy_mcp.server"],
      "env": {
        "WORKFLOWY_API_KEY": "your_api_key_here"
      }
    }
EOF
else
    mkdir -p "$CLAUDE_CONFIG_DIR"
    cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "workflowy": {
      "command": "$(pwd)/venv/bin/python",
      "args": ["-m", "workflowy_mcp.server"],
      "env": {
        "WORKFLOWY_API_KEY": "your_api_key_here"
      }
    }
  }
}
EOF
    echo "✅ Created Claude Desktop configuration"
    echo "⚠️  IMPORTANT: Edit $CLAUDE_CONFIG_FILE and add your WorkFlowy API key"
fi
echo ""

# Test the installation
echo "Testing installation..."
if python -m workflowy_mcp.server --help &> /dev/null; then
    echo "✅ Server module is accessible"
else
    echo "⚠️  Server module test failed, but installation may still work"
fi
echo ""

echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit Claude Desktop config and add your WorkFlowy API key"
echo "2. Restart Claude Desktop to load the MCP server"
echo "3. The WorkFlowy tools will be available in Claude"
echo ""
echo "To run the server manually:"
echo "  source venv/bin/activate"
echo "  python -m workflowy_mcp.server"
echo ""
echo "For more information, see README.md"
echo ""