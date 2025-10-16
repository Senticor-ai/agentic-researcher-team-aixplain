# End-to-End Integration Tests

This directory contains end-to-end integration tests for the MCP server that test the complete workflow with a real FastAPI backend.

## Overview

The E2E tests verify:
- Full workflow: spawn → status → results
- JSON-LD response format compliance
- Error handling with real backend
- Concurrent request handling
- Parameter validation
- Backend unavailability scenarios

## Prerequisites

### 1. FastAPI Backend Running

The E2E tests require the FastAPI backend to be running:

```bash
# Start the backend
./start-backend.sh

# Or manually
cd api
poetry run uvicorn main:app --reload
```

### 2. Backend Health Check

The tests automatically check if the backend is available before running. If the backend is not available, tests will be skipped with a message.

### 3. Environment Variables

Configure the backend URL if not using default:

```bash
export FASTAPI_BASE_URL=http://localhost:8000
```

## Running the Tests

### Run All E2E Tests

```bash
# From project root
pytest mcp_server/tests/test_e2e_integration.py -v

# Or with marker
pytest -m e2e -v
```

### Run Specific Test Classes

```bash
# Test full workflow only
pytest mcp_server/tests/test_e2e_integration.py::TestFullWorkflow -v

# Test spawn functionality
pytest mcp_server/tests/test_e2e_integration.py::TestSpawnAgentTeam -v

# Test status checks
pytest mcp_server/tests/test_e2e_integration.py::TestGetExecutionStatus -v

# Test results retrieval
pytest mcp_server/tests/test_e2e_integration.py::TestGetExecutionResults -v

# Test listing
pytest mcp_server/tests/test_e2e_integration.py::TestListExecutions -v

# Test error handling
pytest mcp_server/tests/test_e2e_integration.py::TestErrorHandling -v

# Test JSON-LD format
pytest mcp_server/tests/test_e2e_integration.py::TestJSONLDFormat -v

# Test concurrent requests
pytest mcp_server/tests/test_e2e_integration.py::TestConcurrentRequests -v
```

### Run Specific Tests

```bash
# Test complete workflow
pytest mcp_server/tests/test_e2e_integration.py::TestFullWorkflow::test_complete_workflow_success -v

# Test backend unavailable
pytest mcp_server/tests/test_e2e_integration.py::TestErrorHandling::test_backend_unavailable -v
```

## Test Structure

### TestFullWorkflow
Tests the complete end-to-end workflow:
1. Spawn an agent team
2. Poll for completion (with timeout)
3. Retrieve results
4. Validate JSON-LD format

**Note**: This test can take 1-3 minutes to complete as it waits for actual agent execution.

### TestSpawnAgentTeam
Tests spawning agent teams with various configurations:
- Minimal parameters (topic only)
- All parameters (topic, goals, interaction_limit)
- Parameter validation errors

### TestGetExecutionStatus
Tests getting execution status:
- Existing executions
- Non-existent executions (404)
- Parameter validation

### TestGetExecutionResults
Tests retrieving execution results:
- Completed executions
- Not completed executions
- Non-existent executions
- Parameter validation

### TestListExecutions
Tests listing executions:
- List all executions
- Filter by topic
- Filter by status
- Pagination (limit, offset)
- Parameter validation

### TestErrorHandling
Tests error scenarios:
- Backend unavailable
- Timeout handling
- HTTP errors

### TestJSONLDFormat
Tests JSON-LD format compliance:
- Spawn response format
- Status response format
- List response format
- Error response format

### TestConcurrentRequests
Tests concurrent request handling:
- Multiple concurrent spawns
- Multiple concurrent status checks

## Test Markers

All tests in this file are marked with `@pytest.mark.e2e`:

```bash
# Run only e2e tests
pytest -m e2e -v

# Exclude e2e tests (default in pytest.ini)
pytest -m "not e2e" -v
```

## Expected Test Duration

- **Fast tests** (validation, errors): < 1 second each
- **Medium tests** (spawn, status, list): 1-5 seconds each
- **Slow tests** (full workflow): 1-3 minutes each

Total suite runtime: ~5-10 minutes (depending on agent execution time)

## Troubleshooting

### Backend Not Available

```
SKIPPED [1] Backend not available at http://localhost:8000
```

**Solution**: Start the FastAPI backend:
```bash
./start-backend.sh
```

### Tests Timeout

```
FAILED test_complete_workflow_success - TimeoutError: Execution did not complete within 180 seconds
```

**Possible causes**:
- Backend is slow or overloaded
- Agent execution is taking longer than expected
- Network issues

**Solutions**:
- Increase timeout in test (edit `max_wait` variable)
- Check backend logs for errors
- Reduce `interaction_limit` in test

### Connection Refused

```
FAILED - httpx.ConnectError: [Errno 61] Connection refused
```

**Solution**: Ensure backend is running on the correct port:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check port
lsof -i :8000
```

### Import Errors

```
ModuleNotFoundError: No module named 'mcp_server'
```

**Solution**: Install the package in development mode:
```bash
cd mcp_server
poetry install
```

## CI/CD Integration

### Skip E2E Tests in CI

By default, pytest.ini excludes e2e tests:

```ini
addopts = -m "not e2e"
```

### Run E2E Tests in CI

To run e2e tests in CI, override the marker filter:

```bash
# GitHub Actions example
pytest -m e2e -v --tb=short
```

Ensure the FastAPI backend is started before running tests:

```yaml
# .github/workflows/test.yml
- name: Start FastAPI backend
  run: |
    ./start-backend.sh &
    sleep 5  # Wait for backend to start

- name: Run E2E tests
  run: pytest -m e2e -v
```

## Writing New E2E Tests

### Test Template

```python
@pytest.mark.asyncio
async def test_my_feature(
    self,
    check_backend_available,
    mcp_server: LibreChatMCPServer
):
    """Test description."""
    # Arrange
    # ...
    
    # Act
    result = await mcp_server.some_method(...)
    
    # Assert
    assert result["@type"] == "ExpectedType"
    assert "expected_field" in result
```

### Best Practices

1. **Use fixtures**: Use `check_backend_available` to skip if backend is down
2. **Validate JSON-LD**: Always check `@context`, `@type`, and required fields
3. **Clean up**: Tests should be independent (no shared state)
4. **Timeouts**: Use reasonable timeouts for async operations
5. **Error cases**: Test both success and error scenarios
6. **Concurrency**: Test concurrent operations when relevant

## Related Documentation

- [MCP Server README](../README.md)
- [FastAPI Client Tests](test_fastapi_client.py)
- [Server Integration Tests](test_server_integration.py)
- [Example Scripts](../examples/)
