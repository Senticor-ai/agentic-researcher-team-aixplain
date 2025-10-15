# Test Failures Analysis

**Date**: 2025-10-15  
**Test Run**: 122 tests (10 e2e excluded by default)  
**Results**: 103 passed, 19 failed, 10 skipped

## Summary

Out of 122 tests run (excluding e2e):
- ✅ **103 passed** (84.4%)
- ❌ **19 failed** (15.6%)
- ⏭️ **10 skipped** (deprecated V1 tests)

## Failure Categories

### Category 1: Integration Tests Requiring Backend (2 failures)
**Status**: Expected failures - tests require API server running

```
FAILED tests/test_entity_extraction.py::test_simple_topic_paris
FAILED tests/test_entity_extraction.py::test_complex_topic_jugendschutz
```

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Root Cause**: These tests make actual HTTP requests to `localhost:8000` but the API server isn't running.

**Fix Options**:
1. Mark with `@pytest.mark.skipif` to check if server is available
2. Add to e2e marker so they're skipped by default
3. Mock the HTTP requests for unit testing

**Recommendation**: Add `@pytest.mark.skipif` decorator:
```python
import requests

def is_api_available():
    try:
        requests.get("http://localhost:8000/api/v1/health", timeout=1)
        return True
    except:
        return False

@pytest.mark.skipif(not is_api_available(), reason="API server not running")
def test_simple_topic_paris():
    ...
```

---

### Category 2: API Return Format Changes (2 failures)
**Status**: Tests need updating - code evolved to return tuples

```
FAILED tests/test_entity_processor.py::test_validate_and_convert_entities
FAILED tests/test_entity_processor.py::test_process_agent_response
```

**Error**: 
- `AssertionError: assert 2 == 1` (expecting single value, got tuple)
- `TypeError: tuple indices must be integers or slices, not str`

**Root Cause**: `EntityProcessor` methods now return `(entities, metrics)` tuple instead of just entities.

**Fix**: Update tests to unpack tuples:
```python
# Old
result = EntityProcessor.validate_and_convert_entities(entities_data)
assert len(result) == 1

# New
entities, metrics = EntityProcessor.validate_and_convert_entities(entities_data)
assert len(entities) == 1
assert 'total_entities' in metrics
```

---

### Category 3: Method Signature Changes (8 failures)
**Status**: Tests need updating - `model` parameter removed

```
FAILED tests/test_google_search_integration.py::TestGoogleSearchIntegration::test_search_agent_has_google_search_tool
FAILED tests/test_google_search_integration.py::TestGoogleSearchIntegration::test_google_search_with_specific_german_topic
FAILED tests/test_mece_decomposition.py::TestMECEDecomposition::test_complex_topic_mece_structure
FAILED tests/test_wikipedia_integration.py::TestWikipediaIntegration::test_wikipedia_agent_creation
FAILED tests/test_wikipedia_integration.py::TestWikipediaIntegration::test_team_with_wikipedia_agent
FAILED tests/test_wikipedia_integration.py::TestWikipediaIntegration::test_team_without_wikipedia_agent
FAILED tests/test_wikipedia_integration_real.py::TestWikipediaIntegrationReal::test_wikipedia_agent_creation
FAILED tests/test_wikipedia_integration_real.py::TestWikipediaIntegrationReal::test_team_with_wikipedia_agent
```

**Error**: `TypeError: TeamConfig.create_team() got an unexpected keyword argument 'model'`

**Root Cause**: The `model` parameter was removed from `TeamConfig` methods. Model selection is now handled internally via `Config.SEARCH_AGENT_MODEL`, etc.

**Fix**: Remove `model` parameter from all test calls:
```python
# Old
team = TeamConfig.create_team(topic=topic, goals=goals, model="testing")
agent = TeamConfig.create_wikipedia_agent(model="testing")

# New
team = TeamConfig.create_team(topic=topic, goals=goals)
agent = TeamConfig.create_wikipedia_agent()
```

---

### Category 4: Wrong Class Reference (1 failure)
**Status**: Simple fix - use correct class

```
FAILED tests/test_wikipedia_integration_real.py::TestWikipediaIntegrationReal::test_wikipedia_tool_configured
```

**Error**: `AttributeError: type object 'TeamConfig' has no attribute 'TOOL_IDS'`

**Root Cause**: `TOOL_IDS` is in `Config` class, not `TeamConfig`.

**Fix**:
```python
# Old
wikipedia_tool_id = TeamConfig.TOOL_IDS.get("wikipedia")

# New
from api.config import Config
wikipedia_tool_id = Config.TOOL_IDS.get("wikipedia")
```

---

### Category 5: Instruction Content Changes (1 failure)
**Status**: Regression test - instruction was intentionally changed

```
FAILED tests/test_instructions_comparison.py::TestEnhancedInstructions::test_feedback_mechanism
```

**Error**: `AssertionError: Extraction summary section missing`

**Root Cause**: The "EXTRACTION SUMMARY:" section was removed from search agent instructions as part of Phase 1 simplification (Search Agent no longer compiles reports).

**Fix Options**:
1. Update test to check for new "SEARCH EFFECTIVENESS NOTES:" section
2. Remove this specific assertion
3. Mark test as expected failure with explanation

**Recommendation**: Update test:
```python
def test_feedback_mechanism(self):
    """Test that feedback mechanism is present"""
    instructions = get_search_agent_instructions("Test Topic")
    
    # Old extraction summary was removed in Phase 1
    # Now we have simplified notes
    assert "SEARCH EFFECTIVENESS NOTES:" in instructions
    assert "Keep notes brief" in instructions
```

---

### Category 6: Mock Configuration Issues (3 failures)
**Status**: Tests need proper mock setup or integration marker

```
FAILED tests/test_google_search_integration.py::TestGoogleSearchIntegration::test_google_search_tool_accessible
FAILED tests/test_google_search_integration.py::TestGoogleSearchIntegration::test_get_tools_includes_google_search
FAILED tests/test_google_search_integration.py::TestGoogleSearchIntegration::test_get_tools_without_google_search
FAILED tests/test_wikipedia_integration_real.py::TestWikipediaIntegrationReal::test_wikipedia_tool_access
```

**Error**: `AssertionError: assert <MagicMock ...> == '65c51c556eb563350f6e1bb1'`

**Root Cause**: Tests are marked as `@pytest.mark.integration` but are getting mocked objects instead of real ones. These tests require actual API access.

**Fix Options**:
1. Remove mocks and let tests use real API (requires API key)
2. Properly configure mocks to return expected values
3. Skip tests if API key not available

**Recommendation**: Add skipif for API key:
```python
import os
import pytest

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("TEAM_API_KEY"), reason="API key required")
def test_google_search_tool_accessible(self):
    google_tool = ToolFactory.get(Config.get_tool_id("google_search"))
    assert google_tool is not None
```

---

## Warnings (10 warnings)
**Status**: Minor - tests return bool instead of None

Tests in `test_search_strategy_unit.py` and `test_task5_instructions_content.py` return boolean values instead of None.

**Fix**: Change `return True/False` to `assert` statements or remove return.

---

## Action Plan

### Priority 1: Quick Fixes (Can be done immediately)
1. ✅ Remove `model` parameter from 8 test calls
2. ✅ Fix `TeamConfig.TOOL_IDS` → `Config.TOOL_IDS`
3. ✅ Update tuple unpacking in 2 entity processor tests
4. ✅ Update instruction comparison test expectations

### Priority 2: Test Improvements (Should be done)
5. ⏭️ Add skipif decorators for tests requiring backend
6. ⏭️ Add skipif decorators for tests requiring API keys
7. ⏭️ Fix return statements in unit tests (warnings)

### Priority 3: Test Organization (Nice to have)
8. ⏭️ Move integration tests requiring backend to e2e marker
9. ⏭️ Review and update mock configurations
10. ⏭️ Add helper functions for checking API availability

---

## Expected Results After Fixes

After implementing Priority 1 fixes:
- **Expected**: ~115-118 passed (95%+)
- **Skipped**: 10-15 (deprecated + no backend/API key)
- **Failed**: 0-5 (only if backend/API unavailable)

---

## Notes

1. **E2E Tests**: Successfully excluded by default (10 tests)
2. **Deprecated Tests**: Properly skipped (10 V1 tests)
3. **Test Markers**: Working correctly for filtering
4. **Test Configuration**: Centralized in `tests/config.py` ✅

The test suite is in good shape overall. Most failures are due to:
- Code evolution (API changes) - expected and fixable
- Missing backend/API keys - expected for integration tests
- One intentional instruction change - needs test update

The marker system is working well and e2e tests are properly excluded by default!
