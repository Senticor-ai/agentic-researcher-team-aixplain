# Test Markers Summary

This document summarizes the pytest markers added to all test files.

## Markers Used

- `@pytest.mark.unit` - Unit tests (no external dependencies, fast)
- `@pytest.mark.integration` - Integration tests (require backend/database)
- `@pytest.mark.e2e` - End-to-end tests (full workflow with external APIs)
- `@pytest.mark.slow` - Tests that take > 10 seconds
- `@pytest.mark.regression` - Regression tests to prevent breaking changes
- `@pytest.mark.skip` - Tests that are skipped with a reason

## Test Files by Category

### Unit Tests (9 files)

1. **test_api.py** - `@pytest.mark.unit`, `@pytest.mark.skip`
   - V1 API tests (deprecated)
   - Status: Skipped

2. **test_direct_entity_processing.py** - `@pytest.mark.unit`
   - Direct entity processing logic
   - No external dependencies

3. **test_entity_processor.py** - `@pytest.mark.unit`
   - EntityProcessor class tests
   - Uses mocks for external dependencies

4. **test_instructions_comparison.py** - `@pytest.mark.regression`
   - Validates instruction changes
   - Prevents regression in entity extraction features

5. **test_mece_decomposition.py** - `@pytest.mark.unit`
   - MECE decomposition logic tests
   - Some tests marked with `@pytest.mark.integration` for database tests

6. **test_phase1_fixes.py** - `@pytest.mark.unit`
   - Phase 1 bug fixes validation
   - Tests configuration and instructions

7. **test_search_strategy_unit.py** - `@pytest.mark.unit`
   - Search strategy logic tests
   - No API server required

8. **test_task5_instructions_content.py** - `@pytest.mark.unit`
   - Validates Task 5 instruction content
   - No API server required

9. **test_team_config.py** - `@pytest.mark.unit`
   - Team configuration tests
   - Uses mocks for external dependencies

### Integration Tests (9 files)

10. **test_agent_integration.py** - `@pytest.mark.integration`, `@pytest.mark.skip`
    - V1 agent integration tests (deprecated)
    - Status: Skipped

11. **test_api_integration.py** - `@pytest.mark.integration`
    - API integration tests with team agent
    - Requires backend running

12. **test_enhanced_extraction.py** - `@pytest.mark.integration`, `@pytest.mark.slow`
    - Enhanced entity extraction tests
    - Requires backend and takes time

13. **test_entity_extraction.py** - `@pytest.mark.integration`, `@pytest.mark.slow`
    - Entity extraction with real topics
    - Requires backend and takes time

14. **test_google_search_integration.py** - Mixed markers
    - Unit tests: `@pytest.mark.unit` for configuration tests
    - Integration tests: `@pytest.mark.integration` for API tests
    - Slow tests: `@pytest.mark.slow` for end-to-end tests

15. **test_improved_prompts.py** - `@pytest.mark.integration`, `@pytest.mark.slow`
    - Tests improved prompts with real API
    - Requires backend and takes time

16. **test_task5_improvements.py** - `@pytest.mark.integration`, `@pytest.mark.slow`
    - Tests Task 5 improvements with real API
    - Requires backend and takes time

17. **test_wikipedia_integration.py** - `@pytest.mark.integration`
    - Wikipedia integration tests
    - Some tests marked with `@pytest.mark.skip` for manual runs

18. **test_wikipedia_integration_real.py** - `@pytest.mark.integration`, `@pytest.mark.slow`
    - Real Wikipedia API tests
    - Requires API key and takes time

### E2E Tests (2 files)

19. **test_e2e_einbuergerung.py** - `@pytest.mark.e2e`, `@pytest.mark.slow`
    - Full E2E test for Einbürgerung topic
    - Marked with `@pytest.mark.skip` for manual runs

20. **test_e2e_integration.py** - `@pytest.mark.e2e`, `@pytest.mark.slow`
    - Full system E2E tests
    - Tests API and UI integration

## Running Tests by Marker

### Run only unit tests (fast)
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Run only e2e tests
```bash
pytest -m e2e
```

### Run all tests except slow ones
```bash
pytest -m "not slow"
```

### Run regression tests only
```bash
pytest -m regression
```

### Run all tests
```bash
pytest
# or
./run_tests.sh all
```

## Test Execution Time Estimates

- **Unit tests**: < 10 seconds total
- **Integration tests**: 1-3 minutes total (without slow tests)
- **Integration tests (with slow)**: 5-10 minutes total
- **E2E tests**: 5-15 minutes total
- **All tests**: 10-20 minutes total

## Notes

1. **Deprecated Tests**: V1 API and agent tests are marked as skipped since we've moved to V2 team agent architecture.

2. **Manual Tests**: Some E2E tests are marked to skip by default and should be run manually when needed.

3. **API Key Requirements**: Some integration and E2E tests require API keys to be configured in `.env` file.

4. **Backend Requirements**: Integration and E2E tests require the backend API to be running.

5. **Mixed Markers**: Some test files (like `test_google_search_integration.py`) have different markers on individual test methods based on their requirements.

## Marker Definitions in pytest.ini

The markers are defined in `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (require backend)
    e2e: End-to-end tests (full workflow)
    slow: Tests that take > 10 seconds
    regression: Regression tests
```

## Next Steps

1. ✅ All tests have appropriate markers
2. ⏭️ Review each test file individually (Phase 1 of spec)
3. ⏭️ Identify redundant or outdated tests
4. ⏭️ Update test documentation
5. ⏭️ Run full test suite and verify all pass or have clear skip reasons
