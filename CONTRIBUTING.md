# Contributing to WorkFlowy MCP Server

Thank you for your interest in contributing to the WorkFlowy MCP Server! This guide will help you get started with development and contribution.

## Code of Conduct

By participating in this project, you agree to be respectful, inclusive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A WorkFlowy account with API access (for integration testing)
- Familiarity with async Python programming

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/vladzima/workflowy-mcp.git
   cd workflowy-mcp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (recommended):
   ```bash
   pre-commit install
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your test API key
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Follow these guidelines:

- **Code Style**: We use Black for formatting, Ruff for linting, and mypy for type checking
- **Type Hints**: All functions should have type hints
- **Docstrings**: All public functions/classes need docstrings (Google style)
- **Tests**: Write tests for all new functionality

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run all tests
pytest

# Run tests with coverage
pytest --cov=workflowy_mcp --cov-report=term-missing
```

### 4. Test Your Changes

#### Unit Tests
```bash
pytest tests/unit/ -xvs
```

#### Contract Tests
```bash
pytest tests/contract/ -xvs
```

#### Integration Tests (requires API key)
```bash
pytest tests/integration/ -xvs
```

#### Performance Tests
```bash
pytest tests/performance/ -xvs
```

### 5. Commit Your Changes

We follow conventional commit format:

```bash
# Features
git commit -m "feat: add support for bulk node operations"

# Bug fixes
git commit -m "fix: handle rate limit errors correctly"

# Documentation
git commit -m "docs: update API reference for list_nodes"

# Tests
git commit -m "test: add unit tests for retry logic"

# Refactoring
git commit -m "refactor: simplify rate limiter implementation"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Test results/coverage report
- Screenshots (if UI changes)

## Project Structure

```
src/workflowy_mcp/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point
├── server.py             # FastMCP server and tool definitions
├── config.py             # Configuration management
├── transport.py          # STDIO transport implementation
├── client/
│   ├── api_client.py     # WorkFlowy API client
│   ├── rate_limit.py     # Rate limiting logic
│   └── retry.py          # Retry with exponential backoff
├── models/
│   ├── node.py           # WorkFlowy node models
│   ├── requests.py       # Request/response models
│   ├── config.py         # Configuration models
│   └── errors.py         # Error models
└── middleware/
    ├── errors.py         # Error handling middleware
    └── logging.py        # Logging middleware
```

## Testing Guidelines

### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
- **Contract Tests** (`tests/contract/`): Test MCP tool contracts
- **Integration Tests** (`tests/integration/`): Test with mocked API
- **Performance Tests** (`tests/performance/`): Ensure <500ms response times

### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestFeatureName:
    """Test suite for feature."""
    
    @pytest.mark.asyncio
    async def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        mock_client = AsyncMock()
        mock_client.method.return_value = expected_data
        
        # Act
        result = await function_under_test()
        
        # Assert
        assert result == expected_result
```

### Test Coverage

We aim for >95% test coverage. Check coverage with:

```bash
pytest --cov=workflowy_mcp --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Adding New Features

### Adding a New MCP Tool

1. **Define the tool** in `src/workflowy_mcp/server.py`:
   ```python
   @mcp.tool()
   async def workflowy_new_tool(
       param1: str,
       param2: Optional[int] = None
   ) -> Dict[str, Any]:
       """Tool description for MCP."""
       # Implementation
   ```

2. **Add contract test** in `tests/contract/test_new_tool.py`

3. **Add integration test** in `tests/integration/`

4. **Update documentation** in README.md

### Adding API Client Methods

1. **Add method** to `src/workflowy_mcp/client/api_client.py`

2. **Add retry logic** if needed

3. **Add rate limiting** if needed

4. **Write unit tests** in `tests/unit/`

## Documentation

### Docstring Format

```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Longer description if needed, explaining behavior,
    edge cases, or important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
        APIError: When API request fails
    """
```

### Updating Documentation

- Update `README.md` for user-facing changes
- Update `CONTRIBUTING.md` for development changes
- Update inline code comments for complex logic
- Update tool descriptions in `server.py`

## Common Development Tasks

### Running the Server Locally

```bash
# With environment file
python -m workflowy_mcp.server

# With explicit configuration
WORKFLOWY_API_KEY=your_key python -m workflowy_mcp.server
```

### Testing with Claude Desktop

1. Update `claude_desktop_config.json` to point to your dev environment
2. Restart Claude Desktop
3. Test your changes interactively

### Debugging

```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable}")

# Set log level
WORKFLOWY_LOG_LEVEL=DEBUG python -m workflowy_mcp.server
```

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Code to profile
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats()
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions will handle PyPI release

## Getting Help

- 🐛 [Issues](https://github.com/vladzima/workflowy-mcp/issues) - Report bugs
- 💡 [Feature Requests](https://github.com/vladzima/workflowy-mcp/issues/new?template=feature_request.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.