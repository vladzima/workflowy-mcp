# WorkFlowy MCP Server

A Model Context Protocol (MCP) server that integrates WorkFlowy's outline and task management capabilities with LLM applications like Claude Desktop.

## Features

- **8 MCP Tools** for complete WorkFlowy node management
- **FastMCP Framework** for reliable MCP implementation  
- **High Performance** with async operations and rate limiting
- **Automatic Retry** with exponential backoff
- **Structured Logging** for debugging and monitoring

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `workflowy_create_node` | Create new nodes with name, notes, and layout mode |
| `workflowy_update_node` | Update existing node properties |
| `workflowy_get_node` | Retrieve a specific node by ID |
| `workflowy_list_nodes` | List nodes with filtering and pagination |
| `workflowy_delete_node` | Delete a node and its children |
| `workflowy_complete_node` | Mark a node as completed |
| `workflowy_uncomplete_node` | Mark a node as uncompleted |
| `workflowy_search_nodes` | Search nodes by text query |

## Quick Start

### Prerequisites

- Python 3.10 or higher
- WorkFlowy account with API access
- Claude Desktop or other MCP-compatible client

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Install the package
pip install workflowy-mcp
```

#### Option 2: Quick Setup Script

```bash
# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/yourusername/workflowy-mcp/main/install.sh | bash

# Or on Windows:
# irm https://raw.githubusercontent.com/yourusername/workflowy-mcp/main/install.ps1 | iex
```

#### Option 3: Manual Installation from Source

```bash
# Clone the repository (if you want to contribute or modify)
git clone https://github.com/vladzima/workflowy-mcp.git
cd workflowy-mcp
pip install -e .
```

### Configuration

1. **Get your WorkFlowy API key**:
   - From [WorkFlowy](https://beta.workflowy.com/api-key)

2. **Configure Claude Desktop or another client**:
   Edit your client configuration (Claude Desktop example):
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

   Add to the `mcpServers` section:
   ```json
   {
     "mcpServers": {
       "workflowy": {
         "command": "python3",
         "args": ["-m", "workflowy_mcp"],
         "env": {
           "WORKFLOWY_API_KEY": "your_actual_api_key_here",
           // Optional settings (uncomment to override defaults):
           // "WORKFLOWY_API_URL": "https://workflowy.com/api/v1",
           // "WORKFLOWY_REQUEST_TIMEOUT": "30",
           // "WORKFLOWY_MAX_RETRIES": "3",
           // "WORKFLOWY_RATE_LIMIT_REQUESTS": "60",
           // "WORKFLOWY_RATE_LIMIT_WINDOW": "60"
         }
       }
     }
   }
   ```

3. **Restart your client** to load the MCP server

## Usage

Once configured, you can use WorkFlowy tools with your agent:

```
"Create a new WorkFlowy node called 'Project Ideas' with todo layout"

"List all my uncompleted tasks"

"Search for nodes containing 'meeting'"

"Mark the node with ID abc123 as completed"

"Update the 'Weekly Goals' node with new notes"
```

## Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=workflowy_mcp

# Run linting
ruff check src/
mypy src/
black src/ --check
```

### Project Structure

```
workflowy-mcp/
├── src/
│   └── workflowy_mcp/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── server.py            # FastMCP server & tools
│       ├── config.py            # Configuration
│       ├── transport.py         # STDIO transport
│       ├── client/
│       │   ├── api_client.py    # WorkFlowy API client
│       │   ├── rate_limit.py    # Rate limiting
│       │   └── retry.py         # Retry logic
│       ├── models/
│       │   ├── node.py          # Node models
│       │   ├── requests.py      # Request models
│       │   ├── config.py        # Config models
│       │   └── errors.py        # Error models
│       └── middleware/
│           ├── errors.py        # Error handling
│           └── logging.py       # Request logging
├── tests/
│   ├── contract/                # Contract tests
│   ├── integration/              # Integration tests
│   ├── unit/                     # Unit tests
│   └── performance/              # Performance tests
├── pyproject.toml                # Project configuration
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guide
├── install.sh                    # Unix/Mac installer
└── install.ps1                   # Windows installer
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/contract/
pytest tests/integration/
pytest tests/performance/

# Run with coverage report
pytest --cov=workflowy_mcp --cov-report=html

# Run with verbose output
pytest -xvs
```

## API Reference

### Node Structure

```python
{
    "id": "unique-node-id",
    "name": "Node name",                  # Text content
    "note": "Node notes/description",     # Optional notes
    "layoutMode": "bullets",              # Display mode: bullets, todo, h1, h2, h3
    "completedAt": null,                  # Completion timestamp (null if not completed)
    "children": [],                       # Child nodes array
    "createdAt": 1234567890,              # Unix timestamp
    "modifiedAt": 1234567890               # Unix timestamp
}
```

### Error Handling

All tools return a consistent error format:
```json
{
    "success": false,
    "error": "error_type",
    "message": "Human-readable error message",
    "context": {...}  // Additional error context
}
```

## Performance

- Automatic rate limiting prevents API throttling
- Token bucket algorithm for smooth request distribution
- Adaptive rate limiting based on API responses
- Connection pooling for efficient HTTP requests

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [Report bugs](https://github.com/vladzima/workflowy-mcp/issues)
- [Request features](https://github.com/vladzima/workflowy-mcp/issues)

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Integrates with [WorkFlowy API](https://beta.workflowy.com/api-reference/)
- Compatible with [Claude Desktop](https://claude.ai/desktop) and other MCP clients