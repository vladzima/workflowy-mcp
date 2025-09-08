# Data Model: WorkFlowy MCP Server

## Core Entities

### WorkFlowyNode
Represents a single node in the WorkFlowy outline hierarchy.

**Fields:**
- `id: str` - Unique identifier for the node
- `nm: str | None` - Name/text content of the node
- `no: str | None` - Note content attached to the node
- `cp: bool` - Completion status (true if completed)
- `ch: List[WorkFlowyNode] | None` - Child nodes (hierarchical structure)
- `created: int` - Creation timestamp (Unix timestamp)
- `modified: int` - Last modification timestamp (Unix timestamp)
- `priority: int | None` - Priority level (0-3, optional)
- `layout_mode: str | None` - Display layout mode

**Validation Rules:**
- `id` must be non-empty string
- `created` and `modified` must be positive integers
- `priority` if present must be 0, 1, 2, or 3
- `cp` defaults to false if not specified

**State Transitions:**
- Uncompleted → Completed (via complete_node)
- Completed → Uncompleted (via uncomplete_node)
- Any state → Deleted (via delete_node)

### NodeCreateRequest
Request payload for creating a new node.

**Fields:**
- `parentId: str | None` - Parent node ID (null for root level)
- `nm: str` - Name/text content (required)
- `no: str | None` - Note content (optional)
- `priority: int | None` - Priority level (optional)

**Validation Rules:**
- `nm` must be non-empty string
- `parentId` if provided must be valid existing node ID
- `priority` if provided must be 0-3

### NodeUpdateRequest
Request payload for updating an existing node.

**Fields:**
- `nm: str | None` - New name/text content
- `no: str | None` - New note content
- `priority: int | None` - New priority level
- `parentId: str | None` - New parent (for moving nodes)

**Validation Rules:**
- At least one field must be provided
- All fields are optional (partial updates supported)
- `parentId` if provided must be valid existing node ID

### NodeListRequest
Request parameters for listing/searching nodes.

**Fields:**
- `parentId: str | None` - Filter by parent node
- `completed: bool | None` - Filter by completion status
- `query: str | None` - Search query for text content
- `limit: int` - Maximum results (default 100)
- `offset: int` - Pagination offset (default 0)

**Validation Rules:**
- `limit` must be positive, max 1000
- `offset` must be non-negative
- `query` if provided performs substring search

### APIConfiguration
Server configuration for WorkFlowy API access.

**Fields:**
- `api_key: str` - WorkFlowy API authentication key
- `base_url: str` - API base URL (default: https://api.workflowy.com)
- `timeout: int` - Request timeout in seconds (default: 30)
- `max_retries: int` - Maximum retry attempts (default: 3)

**Validation Rules:**
- `api_key` must be non-empty string
- `base_url` must be valid HTTPS URL
- `timeout` must be positive integer
- `max_retries` must be non-negative integer

## MCP Tool Schemas

### Tool: workflowy_create_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Node text content"},
    "note": {"type": "string", "description": "Optional note"},
    "parentId": {"type": "string", "description": "Parent node ID"},
    "priority": {"type": "integer", "minimum": 0, "maximum": 3}
  },
  "required": ["name"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "node": {"$ref": "#/definitions/WorkFlowyNode"},
    "success": {"type": "boolean"}
  }
}
```

### Tool: workflowy_update_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "description": "Node ID to update"},
    "name": {"type": "string", "description": "New name"},
    "note": {"type": "string", "description": "New note"},
    "priority": {"type": "integer", "minimum": 0, "maximum": 3},
    "parentId": {"type": "string", "description": "New parent ID"}
  },
  "required": ["id"]
}
```

### Tool: workflowy_get_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "description": "Node ID to retrieve"}
  },
  "required": ["id"]
}
```

### Tool: workflowy_list_nodes
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "parentId": {"type": "string", "description": "Filter by parent"},
    "completed": {"type": "boolean", "description": "Filter by completion"},
    "query": {"type": "string", "description": "Search query"},
    "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
    "offset": {"type": "integer", "minimum": 0}
  }
}
```

### Tool: workflowy_delete_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "description": "Node ID to delete"}
  },
  "required": ["id"]
}
```

### Tool: workflowy_complete_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "description": "Node ID to complete"}
  },
  "required": ["id"]
}
```

### Tool: workflowy_uncomplete_node
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string", "description": "Node ID to uncomplete"}
  },
  "required": ["id"]
}
```

### Tool: workflowy_search_nodes
**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string", "description": "Search query"},
    "includeCompleted": {"type": "boolean", "default": true}
  },
  "required": ["query"]
}
```

## Resource Schemas

### Resource: workflowy_outline
Read-only resource exposing the user's outline structure.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "nodes": {
      "type": "array",
      "items": {"$ref": "#/definitions/WorkFlowyNode"}
    },
    "total": {"type": "integer"},
    "lastUpdated": {"type": "string", "format": "date-time"}
  }
}
```

## Error Response Schema
Standard error response for all operations.

```json
{
  "type": "object",
  "properties": {
    "error": {"type": "string", "description": "Error message"},
    "code": {"type": "string", "description": "Error code"},
    "details": {"type": "object", "description": "Additional error context"}
  },
  "required": ["error", "code"]
}
```

## Relationships

1. **Parent-Child**: Nodes form a tree structure via parentId references
2. **Completion State**: Nodes have binary completion state affecting visibility
3. **Priority Ordering**: Nodes can be ordered by priority within parent

## Data Constraints

1. **Hierarchy Depth**: No hard limit, but deep nesting affects performance
2. **Node Name Length**: Maximum 5000 characters
3. **Note Length**: Maximum 10000 characters
4. **Batch Operations**: Not supported in initial version
5. **Concurrent Modifications**: Last-write-wins semantics