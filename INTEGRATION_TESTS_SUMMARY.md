# Integration Tests Implementation Summary

## Overview

Created comprehensive integration tests that verify the complete agent workflow with real API calls. These tests validate the end-to-end process of entity extraction, validation, enrichment, and quality checking.

## What Was Created

### 1. Integration Test Suite (`tests/test_agent_workflow_integration.py`)

A complete test suite with 5 test cases covering different entity types:

#### Test Cases

1. **`test_person_entity_workflow`** - Dr. Manfred Lucha
   - Tests Person entity extraction and enrichment
   - Validates Wikipedia links and Wikidata ID
   - Checks schema.org compliance
   - Verifies jobTitle and other Person properties
   - Expected: Person entity with @context, @type, sameAs, wikidata_id

2. **`test_organization_entity_workflow`** - Bundesministerium für Umwelt
   - Tests Organization entity extraction
   - Validates official website URLs
   - Checks GovernmentOrganization type suggestion
   - Verifies organizational structure
   - Expected: GovernmentOrganization with proper schema.org structure

3. **`test_event_entity_workflow`** - Klimagipfel 2024
   - Tests Event entity extraction
   - Validates date and location properties
   - Checks ConferenceEvent type suggestion
   - Verifies organizer relationships
   - Expected: ConferenceEvent with startDate, location, organizer

4. **`test_policy_entity_workflow`** - Bundesteilhabegesetz
   - Tests Policy/Legislation entity extraction
   - Validates official documentation URLs
   - Checks Legislation type suggestion
   - Verifies identifier and jurisdiction
   - Expected: Legislation with identifier, datePublished, jurisdiction

5. **`test_validation_metrics`** - Cross-entity metrics
   - Tests validation metrics tracking
   - Validates quality score calculation
   - Checks compliance rates (schema.org, URLs)
   - Verifies enrichment rates (Wikipedia)
   - Expected: Metrics with compliance rates and quality scores

### 2. Documentation (`tests/INTEGRATION_TESTS_README.md`)

Comprehensive documentation covering:
- Test overview and coverage
- Prerequisites (API keys, tools, dependencies)
- How to run tests (all tests, specific tests, with markers)
- Expected output (success and failure examples)
- Test configuration (timeouts, costs)
- Troubleshooting (API keys, tools, timeouts, rate limits)
- CI/CD integration (GitHub Actions example)
- Monitoring and metrics
- Contributing guidelines

### 3. Quick Run Script (`tests/RUN_INTEGRATION_TESTS.sh`)

Bash script for easy test execution:
- Checks for API key
- Loads .env file
- Runs all tests or specific test
- Colored output for better readability
- Usage: `./tests/RUN_INTEGRATION_TESTS.sh [test_name]`

## Complete Workflow Tested

Each integration test verifies this workflow:

```
1. Search Agent
   ↓ Searches for topic
   ↓ Extracts entities
   ↓ Calls Validation Agent
   
2. Validation Agent (First Pass)
   ↓ Validates URLs from search results
   ↓ Reports invalid/inaccessible URLs
   ↓ Search Agent fixes issues
   
3. Wikipedia Agent
   ↓ Enriches entities with Wikipedia data
   ↓ Adds @context, @type, sameAs, wikidata_id
   ↓ Calls Validation Agent
   
4. Validation Agent (Second Pass)
   ↓ Validates schema.org compliance
   ↓ Checks @context, @type, properties
   ↓ Reports issues
   ↓ Wikipedia Agent fixes issues
   
5. Ontology Agent
   ↓ Suggests better schema.org types
   ↓ Suggests relationships
   ↓ Recommends additional properties
   
6. Final Result
   ✓ Validated entities
   ✓ Schema.org compliant
   ✓ Wikipedia enriched
   ✓ Quality scored
```

## Entity Types Covered

| Entity Type | Test Topic | Expected Type | Key Properties |
|-------------|------------|---------------|----------------|
| Person | Dr. Manfred Lucha | Person | name, jobTitle, worksFor, sameAs |
| Organization | Bundesministerium für Umwelt | GovernmentOrganization | name, alternateName, parentOrganization |
| Event | Klimagipfel 2024 | ConferenceEvent | name, startDate, location, organizer |
| Policy | Bundesteilhabegesetz | Legislation | name, identifier, datePublished, jurisdiction |

## How to Run

### Prerequisites

1. **API Key**: Add to `.env` file
   ```bash
   echo "TEAM_API_KEY=your_api_key_here" > .env
   ```

2. **Dependencies**: Install with poetry or pip
   ```bash
   poetry install
   ```

3. **Tool Configuration**: Ensure all tools configured in `api/config.py`

### Run All Tests

```bash
# Using pytest directly
pytest tests/test_agent_workflow_integration.py -v -s

# Using the quick run script
./tests/RUN_INTEGRATION_TESTS.sh
```

### Run Specific Test

```bash
# Using pytest
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_person_entity_workflow -v -s

# Using the quick run script
./tests/RUN_INTEGRATION_TESTS.sh test_person_entity_workflow
```

### Run with Markers

```bash
# Run all integration tests
pytest -m integration -v -s

# Skip integration tests (run only unit tests)
pytest -m "not integration" -v
```

## Expected Results

### Success Indicators

✓ Team created successfully  
✓ Team execution completed  
✓ Entities extracted from search results  
✓ URLs validated and accessible  
✓ Wikipedia data added to entities  
✓ Schema.org compliance validated  
✓ Entity structure validated  
✓ Quality scores calculated  

### Validation Checks

For each entity, tests verify:
- ✓ Has `@context` field with "https://schema.org"
- ✓ Has `@type` field with appropriate schema.org type
- ✓ Has `name` field
- ✓ Has `description` field
- ✓ Has `sameAs` array (if Wikipedia data available)
- ✓ Has `wikidata_id` (if available)
- ✓ Has `validation_status` field
- ✓ All URLs are properly formatted
- ✓ All URLs are accessible

## Cost Considerations

⚠️ **Integration tests cost money** because they use:
- GPT-4o model for all agents
- External tools (Tavily Search, Wikipedia, etc.)
- Multiple API calls per test

**Estimated costs:**
- Single test: ~$0.10-0.20
- Full test suite: ~$0.50-1.00

**Recommendation:** Run integration tests:
- Before major releases
- After significant changes to agent instructions
- Weekly or bi-weekly (not on every commit)
- Manually when needed

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   SKIPPED: TEAM_API_KEY not found
   ```
   Solution: Add API key to `.env` file

2. **Tool Not Configured**
   ```
   ERROR: Failed to retrieve Wikipedia tool
   ```
   Solution: Check tool IDs in `api/config.py`

3. **Timeout**
   ```
   TimeoutError: Agent execution exceeded time limit
   ```
   Solution: Tests may take 5-10 minutes, be patient

4. **Rate Limiting**
   ```
   ERROR: Rate limit exceeded
   ```
   Solution: Wait a few minutes and try again

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:  # Manual trigger

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install poetry && poetry install
      - run: poetry run pytest tests/test_agent_workflow_integration.py -v -s
        env:
          TEAM_API_KEY: ${{ secrets.TEAM_API_KEY }}
```

## Monitoring

### Metrics to Track

1. **Test Success Rate**: % of tests passing over time
2. **Execution Time**: How long tests take (should be < 10 min)
3. **Entity Quality**: Average quality scores from Validation Agent
4. **Compliance Rates**: Schema.org and URL validation rates
5. **Enrichment Rates**: % of entities with Wikipedia data

### Logging

Tests log detailed information:
- Agent creation and configuration
- Team execution steps
- Entity extraction and validation
- Quality scores and metrics
- Errors and warnings

View detailed logs:
```bash
pytest tests/test_agent_workflow_integration.py -v -s --log-cli-level=DEBUG
```

## Next Steps

1. **Run the tests** to verify the complete workflow works
2. **Monitor results** to track entity quality over time
3. **Add more test cases** for other entity types (Topic, etc.)
4. **Set up CI/CD** to run tests automatically
5. **Track metrics** to measure improvement over time

## Files Created

1. `tests/test_agent_workflow_integration.py` - Integration test suite (5 tests)
2. `tests/INTEGRATION_TESTS_README.md` - Comprehensive documentation
3. `tests/RUN_INTEGRATION_TESTS.sh` - Quick run script
4. `INTEGRATION_TESTS_SUMMARY.md` - This summary document

## Benefits

✅ **Validates complete workflow** - Tests all agents working together  
✅ **Real-world scenarios** - Uses actual topics and entities  
✅ **Quality assurance** - Verifies schema.org compliance and validation  
✅ **Regression prevention** - Catches issues before production  
✅ **Documentation** - Shows expected behavior and output  
✅ **Confidence** - Proves the system works end-to-end  

## Conclusion

The integration tests provide comprehensive coverage of the agent workflow with real API calls. They verify that:
- Search Agent finds and extracts entities correctly
- Validation Agent validates URLs and schema.org compliance
- Wikipedia Agent enriches entities with authoritative data
- Ontology Agent suggests semantic improvements
- All agents work together in the hive mind architecture

Run these tests before releases to ensure the system works correctly with real-world data.
