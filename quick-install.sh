#!/bin/bash
# Quick installer for WorkFlowy MCP Server from PyPI

set -e

echo "================================================"
echo "WorkFlowy MCP Server Quick Installer"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+."
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

# Install the package
echo "Installing WorkFlowy MCP Server from PyPI..."
pip install --user workflowy-mcp
echo "✅ WorkFlowy MCP Server installed"
echo ""

# Set up configuration directory
CONFIG_DIR="$HOME/.config/workflowy-mcp"
mkdir -p "$CONFIG_DIR"

# Create config file if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.env" ]; then
    echo "Creating configuration file..."
    cat > "$CONFIG_DIR/config.env" << EOF
# WorkFlowy MCP Server Configuration
WORKFLOWY_API_KEY=your_api_key_here

# Optional configuration
WORKFLOWY_API_BASE_URL=https://beta.workflowy.com/api
WORKFLOWY_REQUEST_TIMEOUT=30
WORKFLOWY_MAX_RETRIES=3
WORKFLOWY_RATE_LIMIT_REQUESTS=60
WORKFLOWY_RATE_LIMIT_WINDOW=60
EOF
    echo "✅ Configuration file created at $CONFIG_DIR/config.env"
    echo "⚠️  IMPORTANT: Edit $CONFIG_DIR/config.env and add your WorkFlowy API key"
else
    echo "ℹ️  Configuration file already exists at $CONFIG_DIR/config.env"
fi
echo ""

# Set up Claude Desktop configuration
echo "Configuring Claude Desktop..."
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Find Python executable path
PYTHON_PATH=$(which python3)

if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "ℹ️  Claude Desktop configuration already exists"
    echo "   Add this to the 'mcpServers' section of $CLAUDE_CONFIG_FILE:"
else
    mkdir -p "$CLAUDE_CONFIG_DIR"
    echo "Creating Claude Desktop configuration..."
    cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
EOF
fi

cat << EOF

    "workflowy": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "workflowy_mcp"],
      "env": {
        "WORKFLOWY_CONFIG_FILE": "$CONFIG_DIR/config.env"
      }
    }

EOF

if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
    echo '  }
}' >> "$CLAUDE_CONFIG_FILE"
    echo "✅ Claude Desktop configuration created"
fi

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit $CONFIG_DIR/config.env and add your WorkFlowy API key"
echo "2. Restart Claude Desktop"
echo "3. The WorkFlowy tools will be available in Claude"
echo ""
echo "To test the installation:"
echo "  python3 -m workflowy_mcp --version"
echo ""