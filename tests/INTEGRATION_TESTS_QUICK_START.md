# Integration Tests - Quick Start Guide

## 🚀 Quick Start (3 Steps)

### 1. Set API Key
```bash
echo "TEAM_API_KEY=your_api_key_here" > .env
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Run Tests
```bash
# Run all tests
./tests/RUN_INTEGRATION_TESTS.sh

# Or run specific test
./tests/RUN_INTEGRATION_TESTS.sh test_person_entity_workflow
```

## 📋 Available Tests

| Test | Entity Type | Topic | Duration |
|------|-------------|-------|----------|
| `test_person_entity_workflow` | Person | Dr. Manfred Lucha | ~2-3 min |
| `test_organization_entity_workflow` | Organization | Bundesministerium für Umwelt | ~2-3 min |
| `test_event_entity_workflow` | Event | Klimagipfel 2024 | ~2-3 min |
| `test_policy_entity_workflow` | Policy | Bundesteilhabegesetz | ~2-3 min |
| `test_validation_metrics` | Metrics | Cross-entity validation | ~2-3 min |

## 🎯 What Gets Tested

```
Search Agent → Validation Agent → Wikipedia Agent → Validation Agent → Ontology Agent
     ↓              ↓                    ↓                  ↓                ↓
  Find entities  Validate URLs    Add Wikipedia      Validate schema   Suggest types
                                  + Wikidata ID      + compliance      + relationships
```

## ✅ Expected Output

```
✓ Team created: 67890abcdef
✓ Team execution completed
✓ Found 5 entities
✓ Found 1 Person entities
✓ Person entity structure validated
✓ TEST PASSED: Person entity workflow completed successfully
```

## 💰 Cost Warning

⚠️ Each test costs ~$0.10-0.20 (uses GPT-4o + external tools)  
⚠️ Full suite costs ~$0.50-1.00  
⚠️ Run sparingly, not on every commit!

## 🔧 Troubleshooting

### API Key Not Found
```bash
# Check .env file exists
cat .env

# Should show: TEAM_API_KEY=your_key
```

### Test Timeout
Tests take 2-3 minutes each. Be patient!

### Tool Not Configured
Check `api/config.py` has all tool IDs configured.

## 📚 Full Documentation

See `tests/INTEGRATION_TESTS_README.md` for complete documentation.

## 🎬 Example Run

```bash
$ ./tests/RUN_INTEGRATION_TESTS.sh test_person_entity_workflow

================================
Agent Workflow Integration Tests
================================

Loading environment from .env
Running specific test: test_person_entity_workflow

tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::test_person_entity_workflow 
================================================================================
Starting integration test
================================================================================
--------------------------------------------------------------------------------
TEST: Person Entity Workflow - Dr. Manfred Lucha
--------------------------------------------------------------------------------

Topic: Dr. Manfred Lucha Minister Baden-Württemberg

1. Creating team with Search, Validation, Wikipedia, and Ontology agents...
✓ Team created: 67890abcdef

2. Research prompt:
Research the following topic and extract key entities...

3. Running team agents...
   Expected workflow:
   - Search Agent searches for Dr. Manfred Lucha
   - Validation Agent validates URLs from search results
   - Wikipedia Agent enriches with Wikipedia data
   - Validation Agent validates schema.org compliance
   - Ontology Agent suggests improvements

✓ Team execution completed

4. Result summary:
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

PASSED

================================
Integration tests complete!
================================
```

## 🎯 Next Steps

1. ✅ Run tests to verify workflow
2. ✅ Check entity quality and validation
3. ✅ Monitor metrics over time
4. ✅ Add to CI/CD pipeline (weekly runs)
5. ✅ Track improvements in entity quality
