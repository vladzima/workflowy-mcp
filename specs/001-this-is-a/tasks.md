# Tasks: WorkFlowy MCP Server

**Input**: Design documents from `/specs/001-this-is-a/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Project structure follows Python package conventions
- Main package: `workflowy_mcp/`

## Phase 3.1: Setup
- [ ] T001 Create Python project structure with src/workflowy_mcp/, tests/, docs/ directories
- [ ] T002 Create pyproject.toml with FastMCP, httpx, pydantic, python-dotenv dependencies
- [ ] T003 [P] Create .env.example with WORKFLOWY_API_KEY placeholder
- [ ] T004 [P] Configure black, mypy, and ruff for code quality
- [ ] T005 [P] Create .gitignore for Python project with venv, __pycache__, .env exclusions

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (MCP Tools)
- [ ] T006 [P] Contract test for workflowy_create_node tool in tests/contract/test_create_node.py
- [ ] T007 [P] Contract test for workflowy_update_node tool in tests/contract/test_update_node.py
- [ ] T008 [P] Contract test for workflowy_get_node tool in tests/contract/test_get_node.py
- [ ] T009 [P] Contract test for workflowy_list_nodes tool in tests/contract/test_list_nodes.py
- [ ] T010 [P] Contract test for workflowy_delete_node tool in tests/contract/test_delete_node.py
- [ ] T011 [P] Contract test for workflowy_complete_node tool in tests/contract/test_complete_node.py
- [ ] T012 [P] Contract test for workflowy_uncomplete_node tool in tests/contract/test_uncomplete_node.py
- [ ] T013 [P] Contract test for workflowy_search_nodes tool in tests/contract/test_search_nodes.py

### Integration Tests (User Stories)
- [ ] T014 [P] Integration test for node creation and retrieval flow in tests/integration/test_node_lifecycle.py
- [ ] T015 [P] Integration test for authentication and error handling in tests/integration/test_auth_errors.py
- [ ] T016 [P] Integration test for search and filtering operations in tests/integration/test_search_filter.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [ ] T017 [P] WorkFlowyNode model with validation in src/workflowy_mcp/models/node.py
- [ ] T018 [P] Request/Response models (NodeCreateRequest, NodeUpdateRequest, etc.) in src/workflowy_mcp/models/requests.py
- [ ] T019 [P] Configuration model (APIConfiguration) in src/workflowy_mcp/models/config.py
- [ ] T020 [P] Error response models in src/workflowy_mcp/models/errors.py

### API Client
- [ ] T021 WorkFlowy API client with httpx in src/workflowy_mcp/client/api_client.py
- [ ] T022 Retry logic with exponential backoff in src/workflowy_mcp/client/retry.py
- [ ] T023 Rate limiting handler in src/workflowy_mcp/client/rate_limit.py

### MCP Server Core
- [ ] T024 FastMCP server initialization in src/workflowy_mcp/server.py
- [ ] T025 Environment configuration loader in src/workflowy_mcp/config.py
- [ ] T026 Logging setup with structured output in src/workflowy_mcp/logging.py

### MCP Tool Implementations
- [ ] T027 Implement workflowy_create_node tool in src/workflowy_mcp/tools/create.py
- [ ] T028 Implement workflowy_update_node tool in src/workflowy_mcp/tools/update.py
- [ ] T029 Implement workflowy_get_node tool in src/workflowy_mcp/tools/get.py
- [ ] T030 Implement workflowy_list_nodes tool in src/workflowy_mcp/tools/list.py
- [ ] T031 Implement workflowy_delete_node tool in src/workflowy_mcp/tools/delete.py
- [ ] T032 Implement workflowy_complete_node tool in src/workflowy_mcp/tools/complete.py
- [ ] T033 Implement workflowy_uncomplete_node tool in src/workflowy_mcp/tools/uncomplete.py
- [ ] T034 Implement workflowy_search_nodes tool in src/workflowy_mcp/tools/search.py

### MCP Resources
- [ ] T035 Implement workflowy_outline resource in src/workflowy_mcp/resources/outline.py

## Phase 3.4: Integration
- [ ] T036 Wire up all tools to FastMCP server in src/workflowy_mcp/__main__.py
- [ ] T037 Add error handling middleware in src/workflowy_mcp/middleware/errors.py
- [ ] T038 Add request/response logging middleware in src/workflowy_mcp/middleware/logging.py
- [ ] T039 Create STDIO transport handler in src/workflowy_mcp/transport.py

## Phase 3.5: Polish
- [ ] T040 [P] Unit tests for models validation in tests/unit/test_models.py
- [ ] T041 [P] Unit tests for retry logic in tests/unit/test_retry.py
- [ ] T042 [P] Unit tests for rate limiting in tests/unit/test_rate_limit.py
- [ ] T043 Performance tests for API operations (<500ms) in tests/performance/test_response_times.py
- [ ] T044 [P] Create comprehensive README.md with installation and usage instructions
- [ ] T045 [P] Create CONTRIBUTING.md with development setup guide
- [ ] T046 Package setup for PyPI distribution in setup.py and MANIFEST.in
- [ ] T047 Create GitHub Actions CI/CD workflow in .github/workflows/ci.yml
- [ ] T048 Manual testing following quickstart.md scenarios

## Dependencies
- Setup tasks (T001-T005) must complete first
- All tests (T006-T016) must be written and failing before implementation
- Models (T017-T020) before API client (T021-T023)
- API client before tool implementations (T027-T034)
- All tools implemented before integration (T036-T039)
- Core complete before polish tasks (T040-T048)

## Parallel Execution Examples

### Contract Tests Launch (T006-T013):
```bash
# Can run all contract tests in parallel as they're independent files
Task: "Contract test for workflowy_create_node tool in tests/contract/test_create_node.py"
Task: "Contract test for workflowy_update_node tool in tests/contract/test_update_node.py"
Task: "Contract test for workflowy_get_node tool in tests/contract/test_get_node.py"
Task: "Contract test for workflowy_list_nodes tool in tests/contract/test_list_nodes.py"
Task: "Contract test for workflowy_delete_node tool in tests/contract/test_delete_node.py"
Task: "Contract test for workflowy_complete_node tool in tests/contract/test_complete_node.py"
Task: "Contract test for workflowy_uncomplete_node tool in tests/contract/test_uncomplete_node.py"
Task: "Contract test for workflowy_search_nodes tool in tests/contract/test_search_nodes.py"
```

### Models Creation (T017-T020):
```bash
# All model files are independent
Task: "WorkFlowyNode model with validation in src/workflowy_mcp/models/node.py"
Task: "Request/Response models in src/workflowy_mcp/models/requests.py"
Task: "Configuration model in src/workflowy_mcp/models/config.py"
Task: "Error response models in src/workflowy_mcp/models/errors.py"
```

### Documentation (T044-T045):
```bash
# Documentation files don't conflict
Task: "Create comprehensive README.md"
Task: "Create CONTRIBUTING.md"
```

## Notes
- [P] tasks = different files, no dependencies
- Each task creates a specific file or modifies a unique section
- Tests MUST fail before implementing (RED phase of TDD)
- Commit after each task with descriptive message
- Follow Python package best practices
- Use type hints throughout for FastMCP schema generation

## Task Generation Rules Applied
1. **From Contracts**: 8 MCP tools → 8 contract test tasks [P]
2. **From Data Model**: 4 entity types → 4 model creation tasks [P]
3. **From User Stories**: 3 main flows → 3 integration test tasks [P]
4. **From Tech Stack**: FastMCP + httpx → specific implementation tasks
5. **Ordering**: Setup → Tests → Models → Client → Tools → Integration → Polish

## Validation Checklist
- [x] All 8 MCP tools have corresponding contract tests
- [x] All 4 entity types have model tasks
- [x] All tests come before implementation (T006-T016 before T017+)
- [x] Parallel tasks modify different files
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] TDD cycle enforced (tests must fail first)