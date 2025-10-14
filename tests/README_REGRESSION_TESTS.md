# Regression Test Suite

## Overview

This document describes the regression tests that ensure implemented features don't degrade over time.

## Test Suites

### Enhanced Entity Extraction (Task 4)

**File:** `tests/test_instructions_comparison.py`

**Purpose:** Prevent regression of enhanced entity extraction features implemented in Task 4.

**Features Tested:**
- ✅ New entity type definitions (TOPIC, EVENT, POLICY)
- ✅ Comprehensive examples in German and English
- ✅ Detailed output formats with dates and identifiers
- ✅ Complete coverage extraction strategy (1.5+ entities per result)
- ✅ Feedback mechanism with entity counts by type
- ✅ German language support
- ✅ Temporal information requirements
- ✅ Policy identifier requirements
- ✅ Complete coverage strategy

**Test Count:** 10 tests

**Run Command:**
```bash
# Run all regression tests
pytest -m regression -v

# Run only enhanced extraction tests
pytest tests/test_instructions_comparison.py -v

# Run with coverage
pytest tests/test_instructions_comparison.py --cov=api.instructions -v
```

**Expected Results:**
```
10 passed in 0.04s
```

## Adding New Regression Tests

When implementing new features that should not regress:

1. **Create test file** in `tests/` directory
2. **Add `@pytest.mark.regression`** decorator to test class
3. **Write specific assertions** that verify the feature
4. **Document in this file** what the tests cover
5. **Run tests** to ensure they pass initially

### Example:

```python
import pytest

@pytest.mark.regression
class TestMyNewFeature:
    """Regression tests for My New Feature"""
    
    def test_feature_is_present(self):
        """Test that the feature exists"""
        result = my_feature_function()
        assert result is not None, "Feature should exist"
    
    def test_feature_behavior(self):
        """Test that the feature behaves correctly"""
        result = my_feature_function("input")
        assert result == "expected", "Feature should work correctly"
```

## CI/CD Integration

These regression tests should be run:
- ✅ On every pull request
- ✅ Before merging to main
- ✅ On scheduled nightly builds
- ✅ Before releases

### GitHub Actions Example:

```yaml
name: Regression Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      - name: Run regression tests
        run: poetry run pytest -m regression -v
```

## Test Maintenance

### When Tests Fail

1. **Investigate immediately** - Regression test failures indicate feature degradation
2. **Check recent changes** - Review commits since last passing test
3. **Fix or update** - Either fix the regression or update tests if intentional change
4. **Document changes** - Update this file if test expectations change

### When to Update Tests

Update regression tests when:
- ✅ Feature is intentionally enhanced (add new tests)
- ✅ Feature behavior intentionally changes (update assertions)
- ✅ Feature is deprecated (mark tests as skipped with reason)

Do NOT update tests to make them pass if:
- ❌ Feature accidentally broke
- ❌ Refactoring changed behavior unintentionally
- ❌ Dependencies changed unexpectedly

## Test Coverage

Current regression test coverage:

| Feature | Tests | Coverage |
|---------|-------|----------|
| Enhanced Entity Extraction | 10 | 100% |
| *Future features* | - | - |

## Related Documentation

- [Enhanced Extraction Testing Guide](./ENHANCED_EXTRACTION_TESTING.md)
- [Task 4 Implementation](./.kiro/specs/enhanced-entity-extraction/)
- [Main Test README](./README.md) (if exists)
