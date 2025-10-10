# Wikipedia Integration Summary

## Overview

Wikipedia integration has been successfully implemented for the Honeycomb OSINT Agent Team System. This feature enriches extracted entities with authoritative Wikipedia links and Wikidata identifiers, enabling better entity verification, deduplication, and knowledge graph integration.

## Implementation Status

### ✅ Completed Tasks

#### Task 10.1: Configure Wikipedia tool in team
- Added Wikipedia tool ID configuration to `api/team_config.py`
- Created `create_wikipedia_agent()` method to instantiate Wikipedia agent
- Updated `create_team()` to optionally include Wikipedia agent
- Added `enable_wikipedia` parameter for team creation
- Updated Mentalist instructions to coordinate Wikipedia agent
- Created comprehensive setup documentation in `docs/WIKIPEDIA_TOOL_SETUP.md`

#### Task 10.2: Implement Wikipedia entity linking
- Added `extract_wikipedia_enrichment()` method to extract Wikipedia data from agent responses
- Implemented `merge_wikipedia_data()` to merge Wikipedia enrichment into entities
- Updated `generate_jsonld_sachstand()` to include Wikipedia data in JSON-LD output
- Added `sameAs`, `wikidata_id`, and `wikipedia_links` fields to entity models
- Implemented Wikidata ID as schema.org `identifier` property in JSON-LD

#### Task 10.3: Test Wikipedia integration end-to-end
- Created comprehensive test suite in `tests/test_wikipedia_integration.py`
- All 6 unit tests pass successfully
- Created demo script `tests/demo_wikipedia_integration.py` showing full workflow
- Documented end-to-end test for real Wikipedia agent (requires tool configuration)

## Architecture

### Wikipedia Agent

The Wikipedia Agent is a user-defined agent that:
- Receives entities extracted by the Search Agent
- Searches Wikipedia for matching articles in multiple languages (de, en, fr)
- Retrieves Wikipedia URLs and Wikidata identifiers
- Returns enrichment data to be merged with entities

### Team Structure with Wikipedia

```
┌─────────────────────────────────────────────────────────┐
│              TEAM AGENT (Built-in Micro Agents)         │
├─────────────────────────────────────────────────────────┤
│  Mentalist → Inspector → Orchestrator → Response Gen    │
└──────────────────────────┬──────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
┌───────────▼──────────┐  ┌──────────────▼────────────┐
│   Search Agent       │  │   Wikipedia Agent         │
│ - Tavily Search      │  │ - Wikipedia tool          │
│ - Extract entities   │  │ - Link to Wikipedia       │
│ - Return sources     │  │ - Get Wikidata IDs        │
└──────────────────────┘  └───────────────────────────┘
```

### Workflow

1. **Search Agent** extracts entities using Tavily Search
2. **Mentalist** reviews extracted entities and assigns Wikipedia Agent
3. **Wikipedia Agent** enriches entities:
   - Searches Wikipedia for each entity
   - Retrieves URLs in multiple languages
   - Extracts Wikidata IDs
4. **EntityProcessor** merges Wikipedia data into entities
5. **JSON-LD output** includes `sameAs` and `identifier` properties

## JSON-LD Output Format

### Without Wikipedia Enrichment
```json
{
  "@type": "Person",
  "name": "Dr. Manfred Lucha",
  "jobTitle": "Minister",
  "citation": [
    {"@type": "WebPage", "url": "https://source.com/article"}
  ]
}
```

### With Wikipedia Enrichment
```json
{
  "@type": "Person",
  "name": "Dr. Manfred Lucha",
  "jobTitle": "Minister",
  "sameAs": [
    "https://de.wikipedia.org/wiki/Manfred_Lucha",
    "https://en.wikipedia.org/wiki/Manfred_Lucha",
    "https://www.wikidata.org/wiki/Q1889089"
  ],
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "Wikidata",
    "value": "Q1889089"
  },
  "citation": [
    {"@type": "WebPage", "url": "https://source.com/article"}
  ]
}
```

## Configuration

### Enable Wikipedia Agent

```python
from api.team_config import TeamConfig

# Create team WITH Wikipedia agent (default)
team = TeamConfig.create_team(
    topic="Dr. Manfred Lucha Baden-Württemberg",
    goals=["Find biographical information"],
    enable_wikipedia=True  # Default
)

# Create team WITHOUT Wikipedia agent
team = TeamConfig.create_team(
    topic="Some topic",
    goals=["Research goals"],
    enable_wikipedia=False
)
```

### Set Wikipedia Tool ID

To enable the Wikipedia agent, configure the tool ID in `api/team_config.py`:

```python
TOOL_IDS = {
    "tavily_search": "6736411cf127849667606689",
    "wikipedia": "YOUR_WIKIPEDIA_TOOL_ID_HERE",  # Get from aixplain marketplace
}
```

See `docs/WIKIPEDIA_TOOL_SETUP.md` for detailed instructions.

## Benefits

1. **Authoritative References**: Wikipedia provides trusted, community-verified information
2. **Multi-language Support**: Links entities across language versions (de, en, fr)
3. **Entity Deduplication**: Wikidata IDs enable identification of duplicate entities across sources
4. **Knowledge Graph Integration**: Wikidata IDs link to broader knowledge graphs (DBpedia, Wikidata)
5. **Entity Verification**: Wikipedia presence confirms entity notability and existence
6. **Schema.org Compliance**: Uses standard `sameAs` and `identifier` properties

## Testing

### Run Unit Tests
```bash
poetry run pytest tests/test_wikipedia_integration.py -v
```

### Run Demo
```bash
poetry run python tests/demo_wikipedia_integration.py
```

### Run End-to-End Test (requires Wikipedia tool configuration)
```bash
poetry run pytest tests/test_wikipedia_integration.py::TestWikipediaIntegration::test_end_to_end_wikipedia_enrichment -v
```

## Files Modified

### Core Implementation
- `api/team_config.py` - Wikipedia agent creation and team configuration
- `api/entity_processor.py` - Wikipedia data extraction and merging
- `api/models.py` - Entity models with Wikipedia fields

### Documentation
- `docs/WIKIPEDIA_TOOL_SETUP.md` - Setup guide
- `docs/WIKIPEDIA_INTEGRATION_SUMMARY.md` - This file

### Tests
- `tests/test_wikipedia_integration.py` - Comprehensive test suite
- `tests/demo_wikipedia_integration.py` - Interactive demo

## Next Steps

1. **Configure Wikipedia Tool ID**: Get the Wikipedia tool ID from aixplain marketplace and update `api/team_config.py`
2. **Test with Real Agent**: Run end-to-end test with actual Wikipedia agent
3. **Verify Multi-language Support**: Test with entities that have Wikipedia articles in multiple languages
4. **Integration Testing**: Test Wikipedia enrichment with various entity types (Person, Organization)
5. **UI Enhancement**: Update UI to display Wikipedia links and Wikidata IDs in entity cards

## Known Limitations

1. **Tool Configuration Required**: Wikipedia agent only works when Wikipedia tool ID is configured
2. **Wikipedia Coverage**: Not all entities have Wikipedia articles
3. **Language Support**: Currently supports de, en, fr - can be extended to more languages
4. **Mentalist Coordination**: Mentalist must decide to invoke Wikipedia agent - not automatic

## Troubleshooting

### Wikipedia Agent Not Created
- Check that `TOOL_IDS["wikipedia"]` is set in `api/team_config.py`
- Verify Wikipedia tool is available in your aixplain account
- See `docs/WIKIPEDIA_TOOL_SETUP.md` for configuration help

### No Wikipedia Links in Output
- Verify Wikipedia agent was created (check logs)
- Check that Mentalist assigned Wikipedia Agent (review intermediate_steps)
- Confirm entities have Wikipedia articles
- Review Wikipedia Agent output in execution logs

## References

- [aixplain Documentation](https://docs.aixplain.com/)
- [Schema.org sameAs Property](https://schema.org/sameAs)
- [Schema.org identifier Property](https://schema.org/identifier)
- [Wikidata](https://www.wikidata.org/)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)
