---
title: Test Suite Refactoring and Organization
status: draft
created: 2025-10-15
priority: high
---

# Test Suite Refactoring and Organization

## Goal

Organize and refactor the test suite to have clear separation between unit, integration, and e2e tests, with proper markers and documentation. Remove redundant tests and ensure all tests are valuable and maintainable.

## Current State

- 20 test files in `tests/` directory
- Mix of unit, integration, and e2e tests without consistent markers
- Some tests may be redundant or outdated
- No clear organization or documentation of what each test covers
- Test runner exists but tests aren't properly categorized

## Success Criteria

- [x] All tests have appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`)
- [ ] Redundant tests removed or consolidated
- [ ] Test suite runs successfully with `./run_tests.sh`
- [ ] Unit tests run in < 10 seconds total
- [ ] Clear documentation of what each test file covers
- [ ] All tests pass or are marked as skip with reason

## Test Files Inventory

### Unit Tests (9 files)

1. **test_api.py**
   - Status: Review needed
   - Purpose: Test API endpoint logic
   - Action: Add `@pytest.mark.unit`, verify no external dependencies

2. **test_direct_entity_processing.py**
   - Status: Review needed
   - Purpose: Test entity processing logic
   - Action: Add `@pytest.mark.unit`, verify mocks are used

3. **test_entity_processor.py**
   - Status: Review needed
   - Purpose: Test EntityProcessor class
   - Action: Add `@pytest.mark.unit`, verify no API calls

4. **test_instructions_comparison.py**
   - Status: Has `@pytest.mark.regression`
   - Purpose: Validate instruction changes don't break functionality
   - Action: Add `@pytest.mark.unit`, keep regression marker

5. **test_mece_decomposition.py**
   - Status: Review needed
   - Purpose: Test MECE decomposition logic
   - Action: Add `@pytest.mark.unit` to unit tests, `@pytest.mark.integration` to integration tests

6. **test_phase1_fixes.py**
   - Status: Has some markers
   - Purpose: Test Phase 1 bug fixes
   - Action: Review if still relevant, add appropriate markers or remove

7. **test_search_strategy_unit.py**
   - Status: Review needed
   - Purpose: Test search strategy logic
   - Action: Add `@pytest.mark.unit`

8. **test_task5_instructions_content.py**
   - Status: Review needed
   - Purpose: Validate instruction content
   - Action: Add `@pytest.mark.unit` or consider removing if redundant

9. **test_team_config.py**
   - Status: Review needed
   - Purpose: Test team configuration
   - Action: Add `@pytest.mark.unit` or `@pytest.mark.integration` based on dependencies

### Integration Tests (9 files)

10. **test_agent_integration.py**
    - Status: Review needed
    - Purpose: Test agent integration
    - Action: Add `@pytest.mark.integration`, verify backend requirement

11. **test_api_integration.py**
    - Status: Review needed
    - Purpose: Test API integration
    - Action: Add `@pytest.mark.integration`, ensure backend checks

12. **test_enhanced_extraction.py**
    - Status: Review needed
    - Purpose: Test enhanced entity extraction
    - Action: Add `@pytest.mark.integration` and `@pytest.mark.slow`

13. **test_entity_extraction.py**
    - Status: Review needed
    - Purpose: Test entity extraction
    - Action: Add `@pytest.mark.integration` and `@pytest.mark.slow`

14. **test_google_search_integration.py**
    - Status: Has `@pytest.mark.integration`
    - Purpose: Test Google Search tool integration
    - Action: Verify all tests have markers, add `@pytest.mark.slow` where appropriate

15. **test_improved_prompts.py**
    - Status: Review needed
    - Purpose: Test prompt improvements
    - Action: Add `@pytest.mark.integration` and `@pytest.mark.slow`

16. **test_task5_improvements.py**
    - Status: Review needed
    - Purpose: Test Task 5 improvements
    - Action: Review if still relevant, add markers or remove

17. **test_wikipedia_integration.py**
    - Status: Has skip markers
    - Purpose: Test Wikipedia integration
    - Action: Add `@pytest.mark.integration`, review skip reasons

18. **test_wikipedia_integration_real.py**
    - Status: Has `@pytest.mark.slow`
    - Purpose: Test real Wikipedia API
    - Action: Add `@pytest.mark.integration`, keep slow marker

### E2E Tests (2 files)

19. **test_e2e_einbuergerung.py**
    - Status: Has `@pytest.mark.integration` and skip
    - Purpose: E2E test for Einbürgerung topic
    - Action: Change to `@pytest.mark.e2e`, review skip reason

20. **test_e2e_integration.py**
    - Status: Review needed
    - Purpose: Full system E2E test
    - Action: Add `@pytest.mark.e2e` and `@pytest.mark.slow`

## Tasks

### Phase 1: Inventory and Analysis (This Spec)

- [x] List all test files
- [x] Categorize by type (unit/integration/e2e)
- [x] Identify current markers
- [ ] Review each test file individually
- [ ] Identify redundant or outdated tests
- [ ] Document purpose of each test file

### Phase 2: Unit Tests Refactoring

For each unit test file:
- [ ] Review test file content
- [ ] Verify no external dependencies (API calls, database, etc.)
- [ ] Add `@pytest.mark.unit` to all test functions
- [ ] Ensure mocks are used for external dependencies
- [ ] Verify tests run fast (< 1 second each)
- [ ] Update docstrings to explain what's being tested
- [ ] Remove or consolidate redundant tests

### Phase 3: Integration Tests Refactoring

For each integration test file:
- [ ] Review test file content
- [ ] Add `@pytest.mark.integration` to all test functions
- [ ] Add backend availability check or skip condition
- [ ] Add `@pytest.mark.slow` if test takes > 10 seconds
- [ ] Verify tests actually test integration points
- [ ] Update docstrings
- [ ] Remove or consolidate redundant tests

### Phase 4: E2E Tests Refactoring

For each e2e test file:
- [ ] Review test file content
- [ ] Add `@pytest.mark.e2e` to all test functions
- [ ] Add `@pytest.mark.slow` marker
- [ ] Add proper skip conditions for missing API keys
- [ ] Verify tests cover complete workflows
- [ ] Update docstrings
- [ ] Consider if test should be manual instead

### Phase 5: Cleanup and Documentation

- [ ] Remove obsolete test files
- [ ] Update `tests/README.md` with current test inventory
- [ ] Ensure all tests pass or have clear skip reasons
- [ ] Run full test suite and verify
- [ ] Update main README.md with testing instructions
- [ ] Create test coverage baseline

## Test File Review Template

For each test file, document:

```markdown
### test_filename.py

**Purpose**: [What does this test file cover?]

**Type**: [unit/integration/e2e]

**Dependencies**: [None/Backend/External APIs]

**Current State**: [passing/failing/skipped]

**Actions Needed**:
- [ ] Add markers
- [ ] Fix failing tests
- [ ] Update docstrings
- [ ] Remove redundant tests
- [ ] Other: [specify]

**Decision**: [keep/refactor/remove]

**Notes**: [Any additional context]
```

## Questions to Answer for Each Test

1. **What is this test actually testing?**
   - Is it clear from the test name and docstring?
   - Is it testing the right thing?

2. **Is this test still relevant?**
   - Does it test current functionality?
   - Or is it testing something that was refactored/removed?

3. **Is this test redundant?**
   - Does another test cover the same functionality?
   - Can it be consolidated?

4. **Is this test properly categorized?**
   - Unit: No external dependencies, fast
   - Integration: Requires backend or database
   - E2E: Full workflow with external APIs

5. **Does this test have value?**
   - Does it catch real bugs?
   - Or is it just testing implementation details?

6. **Is this test maintainable?**
   - Is it easy to understand?
   - Will it break with minor changes?

## Implementation Plan

### Step 1: Create Review Document

Create `tests/TEST_REVIEW.md` with detailed review of each test file using the template above.

### Step 2: Implement Changes

Work through each test file:
1. Add appropriate markers
2. Fix or skip failing tests
3. Remove redundant tests
4. Update documentation

### Step 3: Verify

Run test suite:
```bash
./run_tests.sh unit         # Should pass quickly
./run_tests.sh integration  # Should pass with backend
./run_tests.sh e2e          # Should pass with APIs
./run_tests.sh all          # Full suite
```

### Step 4: Document

Update documentation:
- `tests/README.md` - Test inventory and usage
- `README.md` - Testing section
- `KNOWN_ISSUES.md` - Any test-related issues

## Success Metrics

- Unit tests: < 10 seconds total
- Integration tests: < 2 minutes total
- E2E tests: < 5 minutes total
- Test coverage: > 70% for core modules
- All tests pass or have documented skip reasons
- Clear documentation of what each test covers

## Non-Goals

- Achieving 100% test coverage
- Testing every edge case
- Rewriting all tests from scratch
- Adding new functionality tests (separate effort)

## Dependencies

- Backend must be running for integration/e2e tests
- API keys must be configured for e2e tests
- pytest and pytest-cov must be installed

## Risks

- Some tests may be testing outdated functionality
- Removing tests might reduce coverage temporarily
- Integration tests may be flaky due to external dependencies

## Timeline

- Phase 1 (Inventory): 1-2 hours
- Phase 2 (Unit tests): 2-3 hours
- Phase 3 (Integration tests): 2-3 hours
- Phase 4 (E2E tests): 1-2 hours
- Phase 5 (Cleanup): 1 hour

Total: ~8-12 hours

## Next Steps

1. Review and approve this spec
2. Create `tests/TEST_REVIEW.md` with detailed analysis
3. Start with Phase 2 (Unit tests) as they're fastest to refactor
4. Work through phases sequentially
5. Update documentation as we go

---

**Status**: Ready for review
**Assignee**: TBD
**Estimated Effort**: 8-12 hours
