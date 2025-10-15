# Test Suite Documentation

Comprehensive test suite for the Honeycomb OSINT Agent Team System.

## 📊 Current Status

**Test Results**: ✅ 100% Pass Rate (100/100 passing, 22 skipped, 10 e2e excluded)

| Metric | Count | Notes |
|--------|-------|-------|
| Total Tests | 132 | All test files |
| Passing | 100 | 100% of runnable tests |
| Skipped | 22 | Deprecated + requires API keys |
| E2E (excluded by default) | 10 | Run with `-m e2e` |

## 🚀 Quick Start

```bash
# Run tests (excludes e2e by default)
pytest

# Run only unit tests (fastest - ~10 seconds)
pytest -m unit

# Run integration tests (requires backend)
pytest -m integration

# Run e2e tests (requires backend + API keys)
pytest -m e2e

# Run all tests including e2e
pytest -m ""

# Run without slow tests
pytest -m "not slow"
```

## 📁 Test Organization

### Test Markers

All tests are categorized with pytest markers:

| Marker | Count | Description | Speed |
|--------|-------|-------------|-------|
| `@pytest.mark.unit` | 81 | No external dependencies | < 1s each |
| `@pytest.mark.integration` | 35 | Requires backend running | 1-10s each |
| `@pytest.mark.e2e` | 10 | Full workflow with APIs | 30s-5min each |
| `@pytest.mark.slow` | 18 | Tests taking > 10 seconds | > 10s each |
| `@pytest.mark.regression` | 11 | Prevent feature degradation | Varies |

### Test Files by Category

#### Unit Tests (9 files)
- `test_api.py` - V1 API logic (deprecated, skipped)
- `test_direct_entity_processing.py` - Entity processing
- `test_entity_processor.py` - Entity processor module
- `test_instructions_comparison.py` - Instruction validation (regression)
- `test_mece_decomposition.py` - MECE decomposition logic
- `test_phase1_fixes.py` - Phase 1 bug fixes validation
- `test_search_strategy_unit.py` - Search strategy logic
- `test_task5_instructions_content.py` - Task 5 instruction validation
- `test_team_config.py` - Team configuration

#### Integration Tests (9 files)
- `test_agent_integration.py` - V1 agent integration (deprecated, skipped)
- `test_api_integration.py` - V2 API integration
- `test_enhanced_extraction.py` - Enhanced entity extraction
- `test_entity_extraction.py` - Entity extraction with real topics
- `test_google_search_integration.py` - Google Search tool integration
- `test_improved_prompts.py` - Prompt improvements validation
- `test_task5_improvements.py` - Task 5 improvements validation
- `test_wikipedia_integration.py` - Wikipedia integration
- `test_wikipedia_integration_real.py` - Real Wikipedia API tests

#### E2E Tests (2 files)
- `test_e2e_einbuergerung.py` - Einbürgerung topic full workflow
- `test_e2e_integration.py` - Full system E2E tests

## ⚙️ Configuration

### Environment Variables

Tests read configuration from `.env` file:

```bash
# Required
API_PORT=8080              # Backend API port
API_HOST=0.0.0.0          # Backend API host

# Optional (for integration/e2e tests)
TEAM_API_KEY=xxx          # aixplain API key
TEST_TIMEOUT=120          # Default timeout (seconds)
TEST_SLOW_TIMEOUT=300     # Slow test timeout (seconds)
TEST_POLL_INTERVAL=5      # Polling interval (seconds)
```

**Important**: Tests use `tests/config.py` which reads from `.env` - no hardcoded defaults!

### Test Configuration

- **pytest.ini**: Test discovery, markers, output options
- **tests/config.py**: Centralized test configuration (reads from `.env`)
- **conftest.py**: Shared fixtures and test setup

## 🎯 Running Tests

### Basic Commands

```bash
# Default: Run all tests except e2e (fastest for development)
pytest

# Run specific marker
pytest -m unit
pytest -m integration
pytest -m e2e

# Run specific file
pytest tests/test_entity_processor.py

# Run specific test
pytest tests/test_entity_processor.py::test_receive_entities_from_agent

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

### Advanced Commands

```bash
# Run tests matching pattern
pytest -k "entity"

# Run with coverage
pytest --cov=api --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Collect tests without running
pytest --collect-only

# Show slowest tests
pytest --durations=10
```

## 📝 Test Naming Conventions

### Files
- `test_*.py` - Test files
- `test_e2e_*.py` - E2E test files (clearly identifiable)

### Functions
- `test_*` - Regular tests
- `test_e2e_*` - E2E tests (clearly identifiable in output)

### Classes
- `Test*` - Test classes

**Example**:
```python
# tests/test_e2e_integration.py
class TestE2EIntegration:
    def test_e2e_health_check(self):  # Clear e2e prefix
        ...
```

## ✅ Adding New Tests

### 1. Choose Test Type

Determine which marker(s) your test needs:

- **Unit**: No external dependencies (mocks only)
- **Integration**: Requires backend or database
- **E2E**: Requires full system with external APIs
- **Slow**: Takes > 10 seconds
- **Regression**: Tests a previously fixed bug

### 2. Create Test File

```python
# tests/test_my_feature.py
import pytest

pytestmark = pytest.mark.unit  # Apply to all tests in file

def test_my_function():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### 3. Add Markers

```python
# Single marker
@pytest.mark.unit
def test_unit_function():
    pass

# Multiple markers
@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    pass

# Skip conditionally
@pytest.mark.skipif(not os.getenv("API_KEY"), reason="API key required")
def test_with_api():
    pass

# File-level marker (applies to all tests)
pytestmark = pytest.mark.unit
```

### 4. Follow Best Practices

- ✅ Use descriptive test names
- ✅ One assertion per test (when possible)
- ✅ Use fixtures for setup/teardown
- ✅ Mock external dependencies in unit tests
- ✅ Add docstrings explaining what's tested
- ✅ Keep tests independent (no shared state)
- ✅ Use `tests/config.py` for configuration

## 🔧 Troubleshooting

### Common Issues

#### 1. No Tests Collected
```bash
# Check test discovery
pytest --collect-only

# Verify file/function naming
# Files must be: test_*.py
# Functions must be: test_*
```

#### 2. Import Errors
```bash
# Ensure poetry environment is active
poetry shell
poetry install

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 3. Backend Not Running
```bash
# Integration/E2E tests need backend
# Start backend on port from .env (API_PORT)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

#### 4. API Key Missing
```bash
# Some tests require TEAM_API_KEY in .env
# These tests will be skipped automatically
echo "TEAM_API_KEY=your_key_here" >> .env
```

#### 5. Configuration Errors
```bash
# Ensure .env has required variables
cat .env | grep API_PORT

# Test configuration loading
python -c "from tests.config import API_BASE_URL; print(API_BASE_URL)"
```

## 📚 Key Concepts

### Test Markers

Tests are organized using pytest markers defined in `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (requires backend running)
    e2e: End-to-end tests (requires backend + external APIs)
    slow: Slow running tests
    regression: Regression tests to prevent feature degradation
```

### E2E Tests Excluded by Default

E2E tests are excluded by default to keep test runs fast:

```ini
# pytest.ini
addopts = 
    -m "not e2e"  # Skip e2e tests by default
```

To run e2e tests: `pytest -m e2e`

### Skipped Tests

Tests are skipped for valid reasons:

1. **Deprecated V1 tests** (10 tests) - Old architecture, kept for reference
2. **Requires API keys** (5 tests) - Need `TEAM_API_KEY` in `.env`
3. **Requires backend** (2 tests) - Need API server running
4. **Manual execution** (5 tests) - Marked for manual runs

### Configuration Centralization

All test configuration is centralized in `tests/config.py`:

```python
from tests.config import API_BASE_URL, API_V1_BASE

# No hardcoded URLs in test files!
response = requests.get(f"{API_V1_BASE}/agent-teams")
```

## 🎓 Important Reminders

### For Developers

1. **Always add markers** to new tests (`@pytest.mark.unit`, etc.)
2. **Use `tests/config.py`** for URLs and configuration (no hardcoded values)
3. **Name e2e tests clearly** with `test_e2e_` prefix
4. **Skip tests requiring external deps** with `@pytest.mark.skipif`
5. **Run unit tests frequently** during development (`pytest -m unit`)
6. **Run full suite before commits** (`pytest`)

### For CI/CD

1. **Fast feedback**: Run `pytest -m unit` first
2. **Full validation**: Run `pytest` (excludes e2e by default)
3. **Complete testing**: Run `pytest -m ""` to include e2e
4. **Parallel execution**: Use `pytest -n auto` for speed
5. **Coverage reports**: Use `pytest --cov=api --cov-report=html`

### For Test Maintenance

1. **Update markers** when test requirements change
2. **Keep `tests/config.py` in sync** with `.env` variables
3. **Document skipped tests** with clear reasons
4. **Remove obsolete tests** (or mark as deprecated)
5. **Update this README** when adding new test categories

## 📖 Additional Documentation

- `TEST_MARKERS_SUMMARY.md` - Detailed marker documentation
- `MARKER_IMPLEMENTATION_REPORT.md` - Implementation details
- `FINAL_FIXES_SUMMARY.md` - Recent fixes and improvements
- `TEST_FAILURES_ANALYSIS.md` - Failure analysis and solutions
- `E2E_TEST_NAMING_UPDATE.md` - E2E naming conventions

## 🔍 Test Coverage

Current coverage areas:

- ✅ Entity extraction and validation
- ✅ API endpoints (V2)
- ✅ Team configuration
- ✅ MECE decomposition
- ✅ Search strategies
- ✅ Wikipedia integration
- ✅ Google Search integration
- ✅ Instruction validation
- ✅ Phase 1 bug fixes
- ✅ Task 5 improvements

## 🚦 Test Execution Time

| Test Type | Count | Avg Time | Total Time |
|-----------|-------|----------|------------|
| Unit | 81 | < 1s | ~10s |
| Integration (fast) | 20 | 1-5s | ~60s |
| Integration (slow) | 15 | 10-30s | ~180s |
| E2E | 10 | 30s-5min | ~10min |

**Recommendation**: Run unit tests during development, full suite before commits.

## 📞 Support

If tests fail unexpectedly:

1. Check `.env` configuration
2. Verify backend is running (for integration/e2e)
3. Check API keys are set (for integration/e2e)
4. Review `TEST_FAILURES_ANALYSIS.md`
5. Run with `-v` for verbose output
6. Run with `-s` to see print statements

---

**Last Updated**: 2025-10-15  
**Test Suite Version**: 2.0 (After refactoring)  
**Status**: ✅ All tests passing or properly skipped
