# QuickStart: WorkFlowy MCP Server

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install workflowy-mcp
```

### Option 2: Install with uv
```bash
uv pip install workflowy-mcp
```

### Option 3: Install from Source
```bash
git clone https://github.com/vladzima/workflowy-mcp.git
cd workflowy-mcp
pip install -e .
```

## Configuration

### Step 1: Get Your WorkFlowy API Key
1. Log in to WorkFlowy at https://workflowy.com
2. Navigate to Settings → API
3. Generate or copy your API key

### Step 2: Set Environment Variable
```bash
export WORKFLOWY_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
WORKFLOWY_API_KEY=your-api-key-here
```

## MCP Client Configuration

### Claude Desktop
Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "workflowy": {
      "command": "python",
      "args": ["-m", "workflowy_mcp"],
      "env": {
        "WORKFLOWY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Code
Add to your `.claude/mcp_settings.json`:

```json
{
  "servers": {
    "workflowy": {
      "command": "python",
      "args": ["-m", "workflowy_mcp"],
      "env": {
        "WORKFLOWY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Cursor
Add to your Cursor settings:

```json
{
  "mcp.servers": {
    "workflowy": {
      "command": "python",
      "args": ["-m", "workflowy_mcp"],
      "env": {
        "WORKFLOWY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### VS Code (with MCP Extension)
Add to your VS Code settings:

```json
{
  "mcp.servers": {
    "workflowy": {
      "command": "python",
      "args": ["-m", "workflowy_mcp"],
      "env": {
        "WORKFLOWY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Basic Usage Examples

Once configured, you can use these commands in your MCP client:

### Create a New Node
```
Create a new WorkFlowy node with the text "Project Ideas" under my root outline
```

### List Your Nodes
```
Show me all my WorkFlowy nodes
```

### Search for Content
```
Search WorkFlowy for nodes containing "meeting notes"
```

### Update a Node
```
Update the WorkFlowy node with ID abc123 to say "Completed Project"
```

### Complete a Task
```
Mark the WorkFlowy node with ID xyz789 as completed
```

### Delete a Node
```
Delete the WorkFlowy node with ID def456
```

## Verification Steps

1. **Test Connection**:
   ```
   List my WorkFlowy nodes (limit to 5)
   ```
   Expected: Returns up to 5 nodes from your outline

2. **Test Create**:
   ```
   Create a WorkFlowy node called "Test Node" with note "Testing MCP integration"
   ```
   Expected: Creates the node and returns its ID

3. **Test Search**:
   ```
   Search WorkFlowy for "Test Node"
   ```
   Expected: Finds the node you just created

4. **Test Update**:
   ```
   Update the "Test Node" to "Test Node - Updated"
   ```
   Expected: Updates the node name

5. **Test Complete**:
   ```
   Mark "Test Node - Updated" as completed
   ```
   Expected: Node is marked as completed

6. **Test Delete**:
   ```
   Delete the "Test Node - Updated"
   ```
   Expected: Node is removed from your outline

## Troubleshooting

### "Authentication failed"
- Verify your API key is correct
- Check the environment variable is set: `echo $WORKFLOWY_API_KEY`
- Ensure the API key has not expired

### "Connection refused"
- Check your internet connection
- Verify WorkFlowy API is accessible
- Check if you're behind a proxy/firewall

### "Tool not found"
- Ensure the MCP server is properly configured in your client
- Restart your MCP client after configuration changes
- Verify Python is in your PATH

### "Rate limit exceeded"
- Wait a few minutes before retrying
- The server implements automatic retry with backoff

## Available Tools

- `workflowy_create_node` - Create new nodes
- `workflowy_update_node` - Update existing nodes
- `workflowy_get_node` - Retrieve specific node
- `workflowy_list_nodes` - List nodes with filtering
- `workflowy_delete_node` - Delete nodes
- `workflowy_complete_node` - Mark as completed
- `workflowy_uncomplete_node` - Mark as not completed
- `workflowy_search_nodes` - Search by content

## Resources

- `workflowy_outline` - Read-only view of your outline structure

## Support

- GitHub Issues: https://github.com/vladzima/workflowy-mcp/issues
- Documentation: https://github.com/vladzima/workflowy-mcp/wiki
- WorkFlowy API Docs: https://beta.workflowy.com/api-reference/