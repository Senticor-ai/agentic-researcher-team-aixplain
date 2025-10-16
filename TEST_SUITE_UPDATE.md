# Test Suite Update: Response Generator Format Tests

## Summary

Added comprehensive test coverage for the Response Generator format parsing fix to the test suite.

## New Tests Added

### 1. `tests/test_response_generator_format.py`
**Type**: Unit test  
**Marker**: `@pytest.mark.unit`  
**Purpose**: Simple unit test to verify Response Generator format conversion

**What it tests**:
- Conversion of grouped entity format (Person, Organization, Event, Topic)
- Correct entity count (10 entities total)
- Entity type distribution (3 Person, 3 Organization, 2 Event, 2 Topic)

**Run time**: ~0.01s (very fast)

### 2. `tests/test_response_generator_integration.py`
**Type**: Integration tests  
**Marker**: `@pytest.mark.unit` (no external dependencies)  
**Purpose**: Comprehensive integration testing of the full entity processing pipeline

**Contains 4 test functions**:

1. **`test_convert_grouped_entities()`**
   - Tests conversion from Response Generator format to standard format
   - Verifies all 10 entities are converted correctly
   - Checks entity type distribution

2. **`test_generate_jsonld_sachstand()`**
   - Tests JSON-LD Sachstand generation
   - Validates required fields (@context, @type, name, etc.)
   - Verifies entity types in JSON-LD format
   - Checks entity structure (citations, etc.)

3. **`test_full_pipeline()`**
   - Tests complete pipeline from agent response to JSON-LD
   - Simulates Response Generator output
   - Validates entity validation/filtering
   - Verifies 5 valid entities (after rejecting placeholder URLs)

4. **`test_entity_details()`**
   - Tests that entity details are preserved during conversion
   - Checks Person entity job titles
   - Checks Organization entity URLs
   - Checks Event entity dates

**Run time**: ~0.08s total for all 4 tests

## Test Data

Uses sample data from `tests/data/output-test-sample.json`:
- 3 Person entities (Angela Pittermann, Eva Fast, Melanie Ganz)
- 3 Organization entities (Familienforum Markdorf, Jugendamt Bodenseekreis, Turnverein Markdorf)
- 2 Event entities (30-jähriges Jubiläum, SPIRITS Festival 2025)
- 2 Topic entities (Familienunterstützung, Mehrgenerationenhaus)

## Running the Tests

### Run all unit tests (includes new tests):
```bash
./run_tests.sh unit
```

### Run only the new Response Generator tests:
```bash
python3 -m pytest tests/test_response_generator_format.py tests/test_response_generator_integration.py -v
```

### Run with pytest directly:
```bash
pytest -m unit tests/test_response_generator*.py -v
```

## Test Results

All 5 new tests pass ✅:

```
tests/test_response_generator_format.py::test_response_generator_format PASSED
tests/test_response_generator_integration.py::test_convert_grouped_entities PASSED
tests/test_response_generator_integration.py::test_generate_jsonld_sachstand PASSED
tests/test_response_generator_integration.py::test_full_pipeline PASSED
tests/test_response_generator_integration.py::test_entity_details PASSED
```

## Integration with CI/CD

These tests are now part of the standard test suite and will run:
- ✅ On every commit (via pytest)
- ✅ In CI/CD pipelines (marked as unit tests, no external dependencies)
- ✅ With `./run_tests.sh unit` (default test run)
- ✅ With `./run_tests.sh all` (comprehensive test run)

## Coverage

The new tests provide coverage for:
- ✅ Response Generator format recognition
- ✅ Grouped entity format conversion
- ✅ Entity type mapping (Person, Organization, Event, Topic, Policy)
- ✅ JSON-LD Sachstand generation
- ✅ Entity validation and filtering
- ✅ Entity detail preservation (job titles, URLs, dates)
- ✅ Full pipeline from agent response to JSON-LD output

## Regression Protection

These tests ensure that:
1. The Response Generator format continues to be recognized
2. All entity types are correctly converted
3. Entity details are preserved during conversion
4. JSON-LD output is properly structured
5. The fix for the "4 entities instead of 10" issue doesn't regress

## Files Modified/Created

### Created:
- `tests/test_response_generator_format.py` - Unit test
- `tests/test_response_generator_integration.py` - Integration tests
- `tests/data/output-test-sample.json` - Sample data (already existed)
- `TEST_SUITE_UPDATE.md` - This documentation

### Modified:
- None (tests are additive)

## Notes

- Tests use `@pytest.mark.unit` marker (fast, no external dependencies)
- Tests can be run standalone or via pytest
- Sample data uses some placeholder URLs (example.com) which are correctly rejected by validation
- Tests verify both successful conversion and proper validation filtering
