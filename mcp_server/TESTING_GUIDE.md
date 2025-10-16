# MCP Server Testing Guide

This guide covers all testing approaches for the LibreChat MCP server, from unit tests to end-to-end integration testing.

## Test Structure

```
mcp_server/
├── tests/
│   ├── test_config.py                    # Configuration tests
│   ├── test_fastapi_client.py            # FastAPI client unit tests
│   ├── test_formatters.py                # Response formatter tests
│   ├── test_main.py                      # Main entry point tests
│   ├── test_server_integration.py        # Server integration tests (mocked)
│   ├── test_e2e_integration.py           # E2E tests (real backend)
│   ├── test_librechat_simulation.py      # LibreChat simulation tests
│   └── README_E2E.md                     # E2E testing documentation
├── examples/
│   ├── 00_full_workflow.py               # Complete workflow example
│   ├── 01_spawn_agent_team.py            # Spawn example
│   ├── 02_check_status.py                # Status check example
│   ├── 03_get_results.py                 # Results retrieval example
│   ├── 04_list_executions.py             # List executions example
│   └── mcp.json.example                  # LibreChat configuration example
└── run_e2e_tests.sh                      # E2E test runner script
```

## Test Categories

### 1. Unit Tests

**Purpose**: Test individual components in isolation with mocked dependencies.

**Files**:
- `test_config.py` - Configuration loading and validation
- `test_fastapi_client.py` - HTTP client methods
- `test_formatters.py` - JSON-LD response formatting

**Run**:
```bash
pytest mcp_server/tests/test_config.py -v
pytest mcp_server/tests/test_fastapi_client.py -v
pytest mcp_server/tests/test_formatters.py -v
```

**Characteristics**:
- Fast (< 1 second per test)
- No external dependencies
- Use mocks for HTTP requests
- Test edge cases and error handling

### 2. Integration Tests (Mocked)

**Purpose**: Test component interactions with mocked external services.

**Files**:
- `test_server_integration.py` - Server tool handlers with mocked FastAPI client

**Run**:
```bash
pytest mcp_server/tests/test_server_integration.py -v
```

**Characteristics**:
- Fast (< 1 second per test)
- Mock FastAPI backend responses
- Test tool handler logic
- Test parameter validation
- Test error handling

### 3. End-to-End Integration Tests

**Purpose**: Test complete workflows with real FastAPI backend.

**Files**:
- `test_e2e_integration.py` - Full workflow tests with real backend

**Prerequisites**:
- FastAPI backend must be running
- Backend must be accessible at configured URL

**Run**:
```bash
# Start backend first
./start-backend.sh

# Run E2E tests
pytest mcp_server/tests/test_e2e_integration.py -v

# Or use the convenience script
./mcp_server/run_e2e_tests.sh
```

**Characteristics**:
- Slow (1-5 minutes total)
- Requires running backend
- Tests real HTTP communication
- Tests actual agent execution
- Validates JSON-LD format

### 4. LibreChat Simulation Tests

**Purpose**: Simulate LibreChat interaction patterns without requiring LibreChat installation.

**Files**:
- `test_librechat_simulation.py` - Simulated LibreChat workflows

**Run**:
```bash
pytest mcp_server/tests/test_librechat_simulation.py -v
```

**Characteristics**:
- Medium speed (depends on backend)
- Tests typical user workflows
- Tests concurrent operations
- Tests response displayability
- Validates JSON-LD rendering

## Running Tests

### Run All Tests

```bash
# From project root
pytest mcp_server/tests/ -v

# Exclude E2E tests (default)
pytest mcp_server/tests/ -v -m "not e2e"
```

### Run by Category

```bash
# Unit tests only
pytest mcp_server/tests/ -v -m unit

# Integration tests (mocked)
pytest mcp_server/tests/ -v -m integration

# E2E tests (requires backend)
pytest mcp_server/tests/ -v -m e2e
```

### Run Specific Test Files

```bash
# Configuration tests
pytest mcp_server/tests/test_config.py -v

# FastAPI client tests
pytest mcp_server/tests/test_fastapi_client.py -v

# Server integration tests
pytest mcp_server/tests/test_server_integration.py -v

# E2E tests
pytest mcp_server/tests/test_e2e_integration.py -v

# LibreChat simulation tests
pytest mcp_server/tests/test_librechat_simulation.py -v
```

### Run Specific Test Classes

```bash
# Test spawn functionality
pytest mcp_server/tests/test_e2e_integration.py::TestSpawnAgentTeam -v

# Test full workflow
pytest mcp_server/tests/test_e2e_integration.py::TestFullWorkflow -v

# Test LibreChat workflows
pytest mcp_server/tests/test_librechat_simulation.py::TestLibreChatWorkflow -v
```

### Run Specific Tests

```bash
# Test complete workflow
pytest mcp_server/tests/test_e2e_integration.py::TestFullWorkflow::test_complete_workflow_success -v

# Test error handling
pytest mcp_server/tests/test_e2e_integration.py::TestErrorHandling::test_backend_unavailable -v
```

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests (fast, no dependencies)
- `@pytest.mark.integration` - Integration tests (mocked dependencies)
- `@pytest.mark.e2e` - End-to-end tests (requires backend)
- `@pytest.mark.slow` - Slow tests (> 10 seconds)

### Using Markers

```bash
# Run only unit tests
pytest -m unit -v

# Run integration and unit tests
pytest -m "unit or integration" -v

# Exclude E2E tests
pytest -m "not e2e" -v

# Run only fast tests
pytest -m "not slow" -v
```

## E2E Test Runner Script

The `run_e2e_tests.sh` script provides a convenient way to run E2E tests:

```bash
# Run all E2E tests
./mcp_server/run_e2e_tests.sh

# Run only fast tests (skip full workflow)
./mcp_server/run_e2e_tests.sh --quick

# Run only full workflow test
./mcp_server/run_e2e_tests.sh --full

# Run specific test class
./mcp_server/run_e2e_tests.sh --class TestSpawnAgentTeam

# Run with verbose output
./mcp_server/run_e2e_tests.sh -vv -s
```

The script will:
1. Check if backend is running
2. Offer to start backend if not running
3. Wait for backend to be ready
4. Run the specified tests
5. Report results

## Manual Testing with Examples

The `examples/` directory contains scripts for manual testing:

### Complete Workflow

```bash
cd mcp_server
python examples/00_full_workflow.py "Your Research Topic"
```

This script:
1. Spawns an agent team
2. Polls for completion
3. Retrieves results
4. Displays summary
5. Saves results to file

### Individual Operations

```bash
# Spawn a team
python examples/01_spawn_agent_team.py "Research Topic"

# Check status (use team ID from spawn)
python examples/02_check_status.py <team_id>

# Get results (use team ID from spawn)
python examples/03_get_results.py <team_id>

# List all executions
python examples/04_list_executions.py
```

## Testing LibreChat Integration

### Prerequisites

1. **Install LibreChat**: Follow [LibreChat installation guide](https://docs.librechat.ai/install/installation/index.html)

2. **Configure MCP Server**: Copy and edit the example configuration:
```bash
cp mcp_server/examples/mcp.json.example ~/librechat/mcp.json
# Edit mcp.json to set correct paths
```

3. **Start Backend**:
```bash
./start-backend.sh
```

4. **Start LibreChat**:
```bash
cd ~/librechat
docker-compose up -d  # For Docker installation
# OR
npm start  # For local installation
```

### Manual Testing Checklist

Use the checklist in [LIBRECHAT_INTEGRATION.md](LIBRECHAT_INTEGRATION.md) to verify:

- [ ] Tool discovery
- [ ] spawn_agent_team tool
- [ ] get_execution_status tool
- [ ] get_execution_results tool
- [ ] list_executions tool
- [ ] JSON-LD format
- [ ] Error handling
- [ ] Performance

### Automated LibreChat Simulation

Run the LibreChat simulation tests:

```bash
pytest mcp_server/tests/test_librechat_simulation.py -v
```

These tests simulate LibreChat interaction patterns without requiring actual LibreChat installation.

## Continuous Integration

### GitHub Actions Example

```yaml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd mcp_server
        pip install poetry
        poetry install
    
    - name: Run unit tests
      run: |
        cd mcp_server
        poetry run pytest tests/ -v -m "unit"
    
    - name: Run integration tests
      run: |
        cd mcp_server
        poetry run pytest tests/ -v -m "integration"
    
    - name: Start backend
      run: |
        ./start-backend.sh &
        sleep 10
    
    - name: Run E2E tests
      run: |
        cd mcp_server
        poetry run pytest tests/ -v -m "e2e"
```

## Troubleshooting

### Tests Fail to Import Modules

**Error**: `ModuleNotFoundError: No module named 'mcp_server'`

**Solution**:
```bash
cd mcp_server
poetry install
poetry run pytest tests/ -v
```

### Backend Not Available

**Error**: `SKIPPED [1] Backend not available at http://localhost:8000`

**Solution**:
```bash
# Start the backend
./start-backend.sh

# Verify it's running
curl http://localhost:8000/health
```

### E2E Tests Timeout

**Error**: `TimeoutError: Execution did not complete within 180 seconds`

**Solutions**:
1. Increase timeout in test
2. Reduce interaction_limit
3. Check backend logs for errors
4. Verify backend has sufficient resources

### Connection Refused

**Error**: `httpx.ConnectError: [Errno 61] Connection refused`

**Solutions**:
```bash
# Check if backend is running
lsof -i :8000

# Check backend logs
tail -f backend.log

# Restart backend
./start-backend.sh
```

### Import Errors in Tests

**Error**: `ImportError: cannot import name 'X' from 'mcp_server'`

**Solutions**:
1. Ensure all dependencies are installed
2. Check Python version (requires 3.10+)
3. Reinstall package: `poetry install --no-cache`

## Test Coverage

### Generate Coverage Report

```bash
cd mcp_server
poetry run pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### View Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Unit tests**: > 90% coverage
- **Integration tests**: > 80% coverage
- **Overall**: > 85% coverage

## Best Practices

### Writing Tests

1. **Use descriptive names**: Test names should describe what they test
2. **One assertion per test**: Keep tests focused
3. **Use fixtures**: Reuse common setup code
4. **Test edge cases**: Empty strings, None values, invalid inputs
5. **Test error paths**: Ensure errors are handled gracefully
6. **Mock external services**: Use mocks for unit tests
7. **Clean up**: Tests should be independent

### Test Organization

1. **Group related tests**: Use test classes
2. **Use markers**: Mark tests by category
3. **Document tests**: Add docstrings explaining what's tested
4. **Keep tests fast**: Mock slow operations in unit tests
5. **Separate concerns**: Unit, integration, and E2E tests in separate files

### Running Tests Efficiently

1. **Run fast tests first**: `pytest -m "not slow"`
2. **Run relevant tests**: Use `-k` to filter by name
3. **Use parallel execution**: `pytest -n auto` (requires pytest-xdist)
4. **Skip slow tests during development**: `pytest -m "not e2e"`
5. **Run full suite before commit**: Ensure all tests pass

## Related Documentation

- [MCP Server README](README.md)
- [E2E Testing Guide](tests/README_E2E.md)
- [LibreChat Integration Guide](LIBRECHAT_INTEGRATION.md)
- [Example Scripts](examples/README.md)
