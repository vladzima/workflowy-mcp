# Research Findings: WorkFlowy MCP Server

## Technology Decisions

### 1. MCP Framework Choice
**Decision**: FastMCP  
**Rationale**: 
- Purpose-built for MCP servers with Pythonic design
- Automatic schema generation from type hints
- Built-in support for multiple transport protocols (STDIO, HTTP, SSE)
- Native authentication support
- Active development and documentation

**Alternatives considered**: 
- Building from scratch with MCP SDK - More complex, reinventing patterns FastMCP provides
- Other MCP frameworks - Less mature or less Python-friendly

### 2. Programming Language
**Decision**: Python 3.10+  
**Rationale**: 
- FastMCP requirement
- Excellent async/await support for API operations
- Rich ecosystem for HTTP clients and testing
- Type hints for automatic schema generation

**Alternatives considered**: 
- TypeScript/Node.js - Would require different MCP framework
- Go/Rust - Overkill for this use case, less MCP framework support

### 3. Authentication Method
**Decision**: Environment variable for WorkFlowy API key  
**Rationale**: 
- WorkFlowy uses Bearer token authentication
- Standard secure practice for API keys
- Easy configuration for users
- Compatible with all MCP client environments

**Alternatives considered**: 
- OAuth flow - WorkFlowy doesn't support OAuth
- Config file - Less secure than environment variables
- Prompt for credentials - Poor UX for MCP server

### 4. Package Management
**Decision**: uv (with pip fallback)  
**Rationale**: 
- FastMCP recommended approach
- Modern Python packaging tool
- Fast dependency resolution
- Fallback to pip ensures compatibility

**Alternatives considered**: 
- Poetry - More complex, not FastMCP recommended
- pip only - Works but slower, less modern

### 5. Testing Framework
**Decision**: pytest with pytest-asyncio  
**Rationale**: 
- Python standard for testing
- Excellent async support
- Rich plugin ecosystem
- Good fixture support for test data

**Alternatives considered**: 
- unittest - Less features, more verbose
- nose2 - Less community support

### 6. HTTP Client Library
**Decision**: httpx  
**Rationale**: 
- Modern async HTTP client
- Similar API to requests
- Better async support than aiohttp
- Type hints support

**Alternatives considered**: 
- aiohttp - More complex API
- requests - No async support
- urllib - Too low-level

### 7. Installation Distribution
**Decision**: PyPI package with multiple installation methods  
**Rationale**: 
- Standard Python distribution
- Compatible with all MCP clients
- Easy installation via pip/uv
- Support for development installation

**Alternatives considered**: 
- Docker container - Adds complexity for MCP integration
- GitHub releases only - Less discoverable
- Platform-specific installers - Too much maintenance

### 8. MCP Transport Protocol
**Decision**: STDIO (standard input/output)  
**Rationale**: 
- Universal MCP client support
- Required for Claude Desktop, Claude Code
- Simplest integration approach
- No network configuration needed

**Alternatives considered**: 
- HTTP/SSE - More complex setup for users
- WebSocket - Not all MCP clients support it

### 9. Error Handling Strategy
**Decision**: Graceful degradation with detailed error messages  
**Rationale**: 
- Better user experience
- Helps with debugging
- MCP protocol expects proper error responses
- API issues shouldn't crash server

**Alternatives considered**: 
- Fail fast - Poor UX for intermittent issues
- Silent failures - Makes debugging impossible

### 10. Configuration Management
**Decision**: Environment variables with sensible defaults  
**Rationale**: 
- Standard practice for API keys
- Works across all platforms
- Easy to document
- Secure by default

**Alternatives considered**: 
- JSON config file - More complex, security concerns
- Command-line arguments - Not suitable for MCP servers
- Database storage - Overkill for simple config

## API Capabilities Analysis

### WorkFlowy API Operations
The API supports these core operations:
1. **Node CRUD**: Create, Read, Update, Delete nodes
2. **Node State**: Complete/Uncomplete nodes
3. **Node Hierarchy**: Parent-child relationships
4. **Node Search**: List nodes with filtering
5. **Node Metadata**: Priority, notes, timestamps

### Rate Limiting Considerations
- API documentation doesn't specify rate limits
- Implement exponential backoff for safety
- Cache responses where appropriate
- Batch operations when possible

## Integration Patterns

### MCP Tool Mapping
Each WorkFlowy operation maps to an MCP tool:
- `workflowy_create_node` → Create node
- `workflowy_update_node` → Update node
- `workflowy_get_node` → Retrieve node
- `workflowy_list_nodes` → List nodes
- `workflowy_delete_node` → Delete node
- `workflowy_complete_node` → Complete node
- `workflowy_uncomplete_node` → Uncomplete node
- `workflowy_search_nodes` → Search with query

### Resource Exposure
Expose read-only resources for:
- User's outline structure
- Recent changes
- Node statistics

## Security Considerations

### API Key Protection
- Never log API keys
- Use environment variables
- Validate key format before use
- Clear error messages for missing keys

### Data Privacy
- No caching of user data on disk
- Memory-only session storage
- No telemetry or usage tracking

## Platform Compatibility

### Supported MCP Clients
1. **Claude Desktop** - Full support via STDIO
2. **Claude Code** - Full support via STDIO
3. **Cursor** - Full support via STDIO
4. **VS Code** - Via MCP extension
5. **OpenAI Codex** - Via compatible MCP bridge

### Installation Methods
1. **pip**: `pip install workflowy-mcp`
2. **uv**: `uv pip install workflowy-mcp`
3. **Development**: `git clone && pip install -e .`
4. **MCP config**: Direct GitHub URL in MCP settings

## Performance Targets

### Response Times
- Node operations: < 500ms
- List operations: < 1s
- Search operations: < 2s

### Concurrency
- Handle multiple concurrent requests
- Async operations throughout
- Connection pooling for HTTP client

## Dependencies Summary

### Core Dependencies
- `fastmcp` - MCP framework
- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### Development Dependencies
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `mypy` - Type checking

## Resolved Clarifications

1. **Single vs Multi-user**: Single user per server instance (standard MCP pattern)
2. **Platform compatibility**: All platforms via Python, specific IDE support documented
3. **Connection persistence**: In-memory during server lifetime
4. **Rate limit strategy**: Exponential backoff with jitter
5. **Specific operations**: Full CRUD + complete/uncomplete as per API

## Next Steps
With all technical decisions made and clarifications resolved, we can proceed to Phase 1 (Design & Contracts) to create the data model, API contracts, and initial test structure.