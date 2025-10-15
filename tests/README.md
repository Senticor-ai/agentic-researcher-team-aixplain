# Test Suite

Comprehensive test suite for the Honeycomb OSINT Agent Team System.

## Quick Start

```bash
# Run unit tests (fast, default)
./run_tests.sh

# Run integration tests (requires backend)
./run_tests.sh integration

# Run end-to-end tests (requires backend + APIs)
./run_tests.sh e2e

# Run all tests
./run_tests.sh all

# Run with coverage report
./run_tests.sh coverage
```

## Test Organization

### Test Types

- **Unit Tests** (`@pytest.mark.unit`) - Fast, no external dependencies
  - Test individual functions and classes
  - Use mocks for external dependencies
  - Should run in < 1 second each

- **Integration Tests** (`@pytest.mark.integration`) - Require backend running
  - Test API endpoints
  - Test database operations
  - Test agent configuration
  - Require backend on port 8080 or 8000

- **E2E Tests** (`@pytest.mark.e2e`) - Full system tests
  - Test complete workflows
  - Require backend + external APIs (Tavily, aixplain)
  - May take several minutes
  - Use real API keys

- **Regression Tests** (`@pytest.mark.regression`) - Prevent feature degradation
  - Test previously fixed bugs
  - Test critical functionality
  - Run before releases

- **Slow Tests** (`@pytest.mark.slow`) - Long-running tests
  - Tests that take > 10 seconds
  - Often overlap with e2e tests

## Test Statistics

Current test distribution:
- Unit tests: 9 files
- Integration tests: 9 files
- E2E tests: 2 files
- Regression tests: 1 file
- Slow tests: 6 files

Total: 20 test files

## Running Specific Tests

```bash
# Run only unit tests
poetry run pytest -m "unit"

# Run only integration tests
poetry run pytest -m "integration"

# Run only e2e tests
poetry run pytest -m "e2e"

# Run everything except slow tests
poetry run pytest -m "not slow"

# Run specific test file
poetry run pytest tests/test_entity_processor.py

# Run specific test function
poetry run pytest tests/test_entity_processor.py::test_receive_entities_from_agent

# Run with verbose output
poetry run pytest -v

# Run with output capture disabled (see prints)
poetry run pytest -s
```

## Test Files

### Unit Tests (No External Dependencies)

- `test_api.py` - API endpoint logic
- `test_direct_entity_processing.py` - Entity processing
- `test_entity_processor.py` - Entity processor module
- `test_instructions_comparison.py` - Instruction validation (regression)
- `test_mece_decomposition.py` - MECE decomposition logic
- `test_phase1_fixes.py` - Phase 1 bug fixes
- `test_search_strategy_unit.py` - Search strategy logic
- `test_task5_instructions_content.py` - Instruction content validation
- `test_team_config.py` - Team configuration

### Integration Tests (Require Backend)

- `test_agent_integration.py` - Agent integration
- `test_api_integration.py` - API integration
- `test_enhanced_extraction.py` - Enhanced entity extraction
- `test_entity_extraction.py` - Entity extraction
- `test_google_search_integration.py` - Google Search tool
- `test_improved_prompts.py` - Prompt improvements
- `test_task5_improvements.py` - Task 5 improvements
- `test_wikipedia_integration.py` - Wikipedia integration
- `test_wikipedia_integration_real.py` - Real Wikipedia API

### E2E Tests (Require Backend + APIs)

- `test_e2e_einbuergerung.py` - Einbürgerung topic E2E
- `test_e2e_integration.py` - Full system E2E

## Adding New Tests

### 1. Create Test File

```python
# tests/test_my_feature.py
import pytest

@pytest.mark.unit
def test_my_unit_test():
    """Test description"""
    assert True

@pytest.mark.integration
def test_my_integration_test():
    """Test description - requires backend"""
    # Test code
    pass
```

### 2. Add Appropriate Markers

- `@pytest.mark.unit` - For unit tests
- `@pytest.mark.integration` - For integration tests
- `@pytest.mark.e2e` - For end-to-end tests
- `@pytest.mark.slow` - For tests taking > 10 seconds
- `@pytest.mark.regression` - For regression tests

### 3. Follow Naming Conventions

- File: `test_*.py`
- Class: `Test*`
- Function: `test_*`

## CI/CD Integration

For CI/CD pipelines:

```bash
# Fast feedback (unit tests only)
./run_tests.sh unit

# Full validation (all tests)
./run_tests.sh all

# With coverage
./run_tests.sh coverage
```

## Troubleshooting

### No Tests Collected

- Check test file naming (`test_*.py`)
- Check function naming (`test_*`)
- Check markers are registered in `pytest.ini`

### Backend Not Running

Integration and E2E tests require the backend:

```bash
./start-backend.sh
```

### Import Errors

Ensure you're in the poetry environment:

```bash
poetry shell
poetry install
```

### Slow Tests

Skip slow tests during development:

```bash
poetry run pytest -m "not slow"
```

## Coverage

Generate coverage report:

```bash
./run_tests.sh coverage
```

View HTML report:

```bash
open htmlcov/index.html
```

## Manual Tests

Some tests are marked for manual execution:

- `manual_*.py` - Manual test scripts
- `demo_*.py` - Demo scripts
- `debug_*.py` - Debug utilities
- `verify_*.py` - Verification scripts

These are excluded from automatic test collection.
