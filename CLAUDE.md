# Claude Code Instructions: WorkFlowy MCP Server

## Project Overview
Building an MCP (Model Context Protocol) server that integrates with WorkFlowy's API to enable programmatic interaction with outlines through standardized tools.

## Technology Stack
- **Language**: Python 3.10+
- **Framework**: FastMCP
- **HTTP Client**: httpx (async)
- **Testing**: pytest with pytest-asyncio
- **Package Manager**: uv (with pip fallback)

## Current Implementation Status
- ✅ Phase 0: Research complete
- ✅ Phase 1: Design complete
- ⏳ Phase 2: Task planning ready
- ⏳ Phase 3: Implementation pending
- ⏳ Phase 4: Testing pending

## Key Architectural Decisions
1. **Single Package Structure**: MCP server as standalone Python package
2. **STDIO Transport**: Universal MCP client compatibility
3. **Async Throughout**: All API operations use async/await
4. **Environment-based Config**: API keys via environment variables
5. **TDD Approach**: Tests written before implementation

## MCP Tools Implemented
- `workflowy_create_node` - Create new nodes
- `workflowy_update_node` - Update existing nodes  
- `workflowy_get_node` - Retrieve specific node
- `workflowy_list_nodes` - List nodes with filtering
- `workflowy_delete_node` - Delete nodes
- `workflowy_complete_node` - Mark as completed
- `workflowy_uncomplete_node` - Mark as not completed
- `workflowy_search_nodes` - Search by content

## Testing Strategy
1. **Contract Tests First**: Validate MCP tool schemas
2. **Integration Tests**: Real WorkFlowy API interactions
3. **Unit Tests Last**: Internal logic validation

## Development Workflow
1. Run tests: `pytest tests/`
2. Type check: `mypy src/`
3. Format code: `black src/ tests/`
4. Run server: `python -m workflowy_mcp`

## Environment Setup
```bash
# Required environment variable
export WORKFLOWY_API_KEY="your-api-key"

# Install dependencies
pip install -e ".[dev]"
```

## Recent Changes
- Initial project structure created
- Research phase completed with technology decisions
- Data model and MCP contracts defined

## Constitutional Compliance
- ✅ Library-first approach (MCP server is the library)
- ✅ TDD enforced (tests before implementation)
- ✅ Simple architecture (single package, no abstractions)
- ✅ Observability (structured logging included)