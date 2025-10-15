# Entity Processing Integration Test

## Overview

`test_entity_processing_integration.py` is a comprehensive integration test that validates the complete entity processing pipeline from agent output to UI-ready JSON-LD format.

## What It Tests

### 1. Real Agent Output Format
The test uses actual output from the Llama 3.3 70B agent researching "AWO Karlsruhe gGmbH", which includes:
- **Person Entities**: 2 people with job titles and descriptions
- **Organization Entities**: 1 organization with description
- **Event Entities**: 2 events with dates, locations, and descriptions
- **Topic Entities**: 2 topics with relationships

### 2. Complete Processing Pipeline
Tests the full flow:
```
Agent Output (JSON) 
  → Entity Extraction 
  → Validation 
  → Deduplication 
  → JSON-LD Conversion 
  → UI-Ready Output
```

### 3. Test Cases

#### `test_parse_agent_output_with_entity_groups`
- Verifies parsing of grouped entity format (`"Person Entities"`, `"Organization Entities"`, etc.)
- Validates correct entity counts by type
- Ensures all entity types are extracted

#### `test_full_entity_processing_pipeline`
- Tests complete pipeline from agent response to JSON-LD sachstand
- Validates JSON-LD structure (`@context`, `@type`, `hasPart`)
- Checks validation metrics (total, valid, rejected entities)
- Verifies quality scores

#### `test_entity_types_preserved`
- Ensures all entity types (Person, Organization, Event, Topic) are preserved
- Validates no entity types are lost during processing

#### `test_entity_fields_preserved`
- Verifies type-specific fields are maintained:
  - Person: `jobTitle`
  - Event: `location`, `date`
  - Topic: `about`/`relationship`
- Ensures field mapping is correct

#### `test_sources_converted_to_citations`
- Validates sources are converted to schema.org `citation` format
- Checks citation structure (`@type: WebPage`, `url`)
- Ensures all entities have proper citations

## Running the Tests

```bash
# Run all tests with verbose output
python -m pytest tests/test_entity_processing_integration.py -v -s

# Run specific test
python -m pytest tests/test_entity_processing_integration.py::test_full_entity_processing_pipeline -v -s

# Run with coverage
python -m pytest tests/test_entity_processing_integration.py --cov=api.entity_processor
```

## Expected Output

```
Extracted entities:
  - Persons: 2
  - Organizations: 1
  - Events: 2
  - Topics: 2

Validation metrics:
  - Total entities: 7
  - Valid entities: 7
  - Rejected entities: 0
  - Avg quality score: 0.70

Entity types found: {'Person', 'Organization', 'Topic', 'Event'}

Sample Person entity: Markus Barton
Sample Event entity: Quartiersfest im Mühlburger Feld
Sample Topic entity: Soziale Dienstleistungen

Entities with citations: 7/7
```

## What This Validates

✅ **Grouped entity format parsing** - Handles agent output with entities grouped by type  
✅ **All entity types supported** - Person, Organization, Event, Topic, Policy  
✅ **Field preservation** - Type-specific fields are maintained  
✅ **Source conversion** - Sources converted to schema.org citations  
✅ **JSON-LD compliance** - Output follows schema.org standards  
✅ **Validation pipeline** - Quality scoring and rejection works  
✅ **UI compatibility** - Output format matches UI expectations  

## Integration with CI/CD

This test should be run:
- Before deploying to production
- After changes to entity processing logic
- After changes to entity models
- After changes to JSON-LD generation

## Troubleshooting

If tests fail:

1. **Check entity counts**: Verify the mock data hasn't changed
2. **Check field names**: Ensure field mapping is correct (e.g., `job_title` → `jobTitle`)
3. **Check JSON-LD structure**: Validate `@context` and `@type` fields
4. **Check logs**: Run with `-s` flag to see detailed output

## Related Files

- `api/entity_processor.py` - Main processing logic
- `api/models.py` - Entity models (PersonEntity, OrganizationEntity, etc.)
- `api/entity_validator.py` - Validation logic
- `ui/src/components/EntitiesDisplay.jsx` - UI component that displays entities
