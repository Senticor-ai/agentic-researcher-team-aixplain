# Integration Tests for Agent Workflow

This directory contains integration tests that verify the complete agent workflow with real API calls.

## Overview

The integration tests verify the end-to-end workflow:
1. **Search Agent** finds entities for specific topics
2. **Validation Agent** validates URLs immediately after search
3. **Wikipedia Agent** enriches entities with Wikipedia data
4. **Validation Agent** validates schema.org compliance after enrichment
5. **Ontology Agent** suggests improvements (better types, relationships)

## Test Coverage

### Entity Types Tested

1. **Person Entity** - `Dr. Manfred Lucha`
   - Tests biographical information extraction
   - Validates Wikipedia enrichment
   - Checks schema.org Person type
   - Verifies jobTitle and worksFor properties

2. **Organization Entity** - `Bundesministerium für Umwelt`
   - Tests government organization extraction
   - Validates official website URLs
   - Checks GovernmentOrganization type suggestion
   - Verifies organizational structure

3. **Event Entity** - `Klimagipfel 2024`
   - Tests event information extraction
   - Validates date and location properties
   - Checks ConferenceEvent type suggestion
   - Verifies organizer relationships

4. **Policy Entity** - `Bundesteilhabegesetz`
   - Tests legislation information extraction
   - Validates official documentation URLs
   - Checks Legislation type suggestion
   - Verifies identifier and jurisdiction properties

5. **Validation Metrics** - Cross-entity metrics
   - Tests validation metrics tracking
   - Validates quality score calculation
   - Checks compliance rates
   - Verifies enrichment rates

## Prerequisites

### 1. API Key Configuration

You need an aixplain API key to run integration tests:

```bash
# Create .env file in project root
echo "TEAM_API_KEY=your_api_key_here" > .env
```

Get your API key from: https://platform.aixplain.com/

### 2. Tool Configuration

Ensure all tools are configured in `api/config.py`:
- Tavily Search tool
- Google Search tool (backup)
- Wikipedia tool
- Schema.org Validator tool
- URL Verifier tool

### 3. Python Dependencies

```bash
# Install dependencies
poetry install

# Or with pip
pip install -r requirements.txt
```

## Running Integration Tests

### Run All Integration Tests

```bash
# Run all integration tests with verbose output
pytest tests/test_agent_workflow_integration.py -v -s

# Run with detailed logging
pytest tests/test_agent_workflow_integration.py -v -s --log-cli-level=INFO
```

### Run Specific Test Cases

```bash
# Test Person entity workflow only
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_person_entity_workflow -v -s

# Test Organization entity workflow only
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_organization_entity_workflow -v -s

# Test Event entity workflow only
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_event_entity_workflow -v -s

# Test Policy entity workflow only
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_policy_entity_workflow -v -s

# Test validation metrics only
pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_validation_metrics -v -s
```

### Run with Pytest Markers

```bash
# Run all integration tests (marked with @pytest.mark.integration)
pytest -m integration -v -s

# Run all slow tests (marked with @pytest.mark.slow)
pytest -m slow -v -s

# Skip integration tests (run only unit tests)
pytest -m "not integration" -v
```

## Expected Output

### Successful Test Output

```
tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_person_entity_workflow 
================================================================================
Starting integration test
================================================================================
--------------------------------------------------------------------------------
TEST: Person Entity Workflow - Dr. Manfred Lucha
--------------------------------------------------------------------------------

Topic: Dr. Manfred Lucha Minister Baden-Württemberg
Goals: ['Find biographical information', 'Identify official role and ministry', 'Get Wikipedia and Wikidata links']

1. Creating team with Search, Validation, Wikipedia, and Ontology agents...
✓ Team created: 67890abcdef

2. Research prompt:
Research the following topic and extract key entities (Person, Organization, Events, Topics):

Topic: Dr. Manfred Lucha Minister Baden-Württemberg...

3. Running team agents...
   Expected workflow:
   - Search Agent searches for Dr. Manfred Lucha
   - Validation Agent validates URLs from search results
   - Wikipedia Agent enriches with Wikipedia data
   - Validation Agent validates schema.org compliance
   - Ontology Agent suggests improvements

✓ Team execution completed

4. Result summary:
   Result type: <class 'str'>
   Parsed JSON with 3 keys
   Found 5 entities
   Found 1 Person entities

5. Person entity validation:
   Name: Dr. Manfred Lucha
   Type: Person
   Has @context: ✓
   Has sameAs: ✓
   Has wikidata_id: ✓
   Validation status: validated

✓ Person entity structure validated

✓ TEST PASSED: Person entity workflow completed successfully
================================================================================
Integration test complete
================================================================================
PASSED
```

### Test Failure Output

If a test fails, you'll see detailed error information:

```
✗ Team execution failed: Agent timeout after 300 seconds

Traceback (most recent call last):
  File "tests/test_agent_workflow_integration.py", line 123, in test_person_entity_workflow
    result = team.run(prompt)
  ...
TimeoutError: Agent execution exceeded time limit
```

## Test Configuration

### Timeouts

Integration tests may take several minutes to complete because they:
- Make real API calls to search engines
- Wait for agent responses
- Process multiple entities
- Validate URLs (HTTP requests)
- Enrich with Wikipedia data

Default timeouts:
- Agent execution: 300 seconds (5 minutes)
- HTTP requests: 30 seconds
- Team execution: 600 seconds (10 minutes)

### Cost Considerations

⚠️ **Integration tests cost money** because they:
- Use GPT-4o model for agents (Search, Wikipedia, Validation, Ontology)
- Make multiple API calls per test
- Use external tools (Tavily Search, Wikipedia, etc.)

Estimated cost per test run:
- Person entity test: ~$0.10-0.20
- Organization entity test: ~$0.10-0.20
- Event entity test: ~$0.10-0.20
- Policy entity test: ~$0.10-0.20
- Full test suite: ~$0.50-1.00

**Recommendation**: Run integration tests sparingly, not on every commit.

## Troubleshooting

### API Key Issues

```
SKIPPED [1] tests/test_agent_workflow_integration.py:18: TEAM_API_KEY not found - skipping integration tests
```

**Solution**: Add your API key to `.env` file:
```bash
echo "TEAM_API_KEY=your_api_key_here" > .env
```

### Tool Configuration Issues

```
ERROR: Failed to retrieve Wikipedia tool: Tool not found
```

**Solution**: Check tool IDs in `api/config.py`:
```python
TOOL_IDS = {
    "tavily_search": "your_tavily_tool_id",
    "wikipedia": "your_wikipedia_tool_id",
    "schema_validator": "your_schema_validator_tool_id",
    "url_verifier": "your_url_verifier_tool_id"
}
```

### Timeout Issues

```
TimeoutError: Agent execution exceeded time limit
```

**Solution**: Increase timeout in test or reduce interaction limit:
```python
team = TeamConfig.create_team(
    topic=topic,
    goals=goals,
    enable_validation=True,
    enable_wikipedia=True,
    enable_ontology=True
)
```

### Rate Limiting

```
ERROR: Rate limit exceeded for API calls
```

**Solution**: Wait a few minutes and try again, or reduce test frequency.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Run weekly on Sunday
  workflow_dispatch:  # Allow manual trigger

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run integration tests
        env:
          TEAM_API_KEY: ${{ secrets.TEAM_API_KEY }}
        run: |
          poetry run pytest tests/test_agent_workflow_integration.py -v -s
```

### Best Practices for CI/CD

1. **Run on schedule** (e.g., nightly or weekly) instead of every commit
2. **Use secrets** for API keys, never commit them
3. **Set timeouts** to prevent hanging builds
4. **Cache dependencies** to speed up builds
5. **Notify on failures** via Slack, email, etc.

## Monitoring and Metrics

### What to Monitor

1. **Test Success Rate**: % of tests passing
2. **Execution Time**: How long tests take
3. **Entity Quality**: Quality scores from Validation Agent
4. **Compliance Rates**: Schema.org and URL validation rates
5. **Enrichment Rates**: % of entities with Wikipedia data

### Logging

Integration tests log detailed information:
- Agent creation and configuration
- Team execution steps
- Entity extraction and validation
- Quality scores and metrics
- Errors and warnings

View logs with:
```bash
pytest tests/test_agent_workflow_integration.py -v -s --log-cli-level=DEBUG
```

## Contributing

When adding new integration tests:

1. **Follow naming convention**: `test_<entity_type>_entity_workflow`
2. **Add docstrings**: Explain expected workflow and entity structure
3. **Log progress**: Use logger.info() for key steps
4. **Validate results**: Assert on entity structure and validation status
5. **Handle errors**: Use try/except and pytest.fail() for clear error messages

## Related Documentation

- [Agent Instructions](../api/instructions/) - Agent system prompts
- [Team Configuration](../api/team_config.py) - Team setup and agent creation
- [Validation Tools](../api/schema_org_validator_tool.py) - Schema.org and URL validation
- [Requirements](../.kiro/specs/schema-org-validation-and-enrichment/requirements.md) - Feature requirements
- [Design](../.kiro/specs/schema-org-validation-and-enrichment/design.md) - Architecture and design

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review agent instructions in `api/instructions/`
3. Check logs with `--log-cli-level=DEBUG`
4. Open an issue with test output and error messages
