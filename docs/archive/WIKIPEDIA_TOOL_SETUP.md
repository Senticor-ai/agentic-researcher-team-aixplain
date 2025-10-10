# Wikipedia Tool Setup Guide

This document explains how to configure the Wikipedia tool for entity enrichment in the Honeycomb OSINT system.

## Overview

The Wikipedia Agent enriches extracted entities by:
- Searching Wikipedia for matching articles in multiple languages (de, en, fr)
- Retrieving Wikipedia URLs for authoritative references
- Extracting Wikidata IDs for entity deduplication
- Adding `sameAs` properties to entities in JSON-LD output

## Wikipedia Tool ID

The Wikipedia tool is now configured with ID: `6633fd59821ee31dd914e232`

This tool is available in the aixplain marketplace and provides Wikipedia search functionality.

### Current Configuration

In `api/team_config.py`:

```python
TOOL_IDS = {
    "tavily_search": "6736411cf127849667606689",
    "wikipedia": "6633fd59821ee31dd914e232",  # Wikipedia tool from aixplain
}
```

### Verifying the Tool

You can verify the Wikipedia tool is accessible:

```python
from aixplain.factories import ToolFactory

# Get Wikipedia tool
wikipedia_tool = ToolFactory.get("6633fd59821ee31dd914e232")
print(f"Tool name: {wikipedia_tool.name}")
print(f"Tool ID: {wikipedia_tool.id}")

# Test search
result = wikipedia_tool.run({"text": "Manfred Lucha"})
print(f"Search result: {result.data[:200]}...")
```

## Configuration

### Enable Wikipedia Agent

By default, the Wikipedia agent is enabled when creating a team. You can control this with the `enable_wikipedia` parameter:

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

### Verify Configuration

To verify the Wikipedia tool is configured correctly:

```bash
cd api
poetry run python -c "from team_config import TeamConfig; print('Wikipedia tool ID:', TeamConfig.TOOL_IDS['wikipedia'])"
```

If the output shows `None`, the Wikipedia tool is not configured and the Wikipedia agent will be skipped.

## How It Works

### Team Architecture with Wikipedia Agent

```
┌─────────────────────────────────────────────────────────┐
│              TEAM AGENT (Built-in Micro Agents)         │
├─────────────────────────────────────────────────────────┤
│  Mentalist → Inspector → Orchestrator → Response Gen    │
└──────────────────────────────┬──────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
┌───────────────▼──────────┐  ┌──────────────▼────────────┐
│     Search Agent         │  │   Wikipedia Agent         │
│  - Tavily Search tool    │  │  - Wikipedia tool         │
│  - Extract entities      │  │  - Link to Wikipedia      │
│  - Return with sources   │  │  - Get Wikidata IDs       │
└──────────────────────────┘  └───────────────────────────┘
```

### Workflow

1. **Search Agent** extracts entities using Tavily Search
2. **Mentalist** reviews extracted entities
3. **Mentalist** assigns **Wikipedia Agent** to enrich entities
4. **Wikipedia Agent** searches Wikipedia for each entity:
   - Searches in multiple languages (de, en, fr)
   - Retrieves Wikipedia URLs
   - Extracts Wikidata IDs
5. **Inspector** reviews enriched entities
6. **Response Generator** creates final output with Wikipedia links

### Example Output

Without Wikipedia Agent:
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

With Wikipedia Agent:
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
  "citation": [
    {"@type": "WebPage", "url": "https://source.com/article"}
  ]
}
```

## Troubleshooting

### Wikipedia Agent Not Created

If you see this warning in logs:
```
WARNING: Wikipedia tool ID not configured - skipping Wikipedia agent creation
```

**Solution**: Configure the Wikipedia tool ID in `api/team_config.py` as described above.

### Wikipedia Tool Not Found

If you see this error:
```
ERROR: Failed to get Wikipedia tool: Model GET Error
```

**Possible causes**:
1. Tool ID is incorrect
2. Tool is not available in your aixplain account
3. Tool requires additional permissions

**Solution**: Verify the tool ID and contact aixplain support if needed.

### No Wikipedia Links in Output

If entities are extracted but no Wikipedia links appear:

1. Check that Wikipedia agent was created (look for log: "Wikipedia agent added to team")
2. Verify the Mentalist assigned the Wikipedia Agent (check intermediate_steps)
3. Check if Wikipedia articles exist for the entities (some entities may not have Wikipedia pages)
4. Review Wikipedia Agent output in execution logs

## Benefits of Wikipedia Integration

1. **Authoritative References**: Wikipedia provides trusted, community-verified information
2. **Multi-language Support**: Links entities across language versions (de, en, fr)
3. **Deduplication**: Wikidata IDs enable identification of duplicate entities
4. **Knowledge Graph Integration**: Wikidata IDs link to broader knowledge graphs
5. **Entity Verification**: Wikipedia presence confirms entity notability and existence

## Next Steps

After configuring Wikipedia tool:
1. Test with known entities (e.g., "Dr. Manfred Lucha")
2. Verify Wikipedia links appear in JSON-LD output
3. Check Wikidata IDs are captured correctly
4. Test with multi-language topics (German and English)

See `tests/test_wikipedia_integration.py` for test examples.
