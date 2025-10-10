# Google Search Integration

## Overview

Google Search has been integrated as a backup tool to Tavily Search in the OSINT Agent Team System. This provides more comprehensive coverage, especially for government websites, official sources, and German regional topics.

## Configuration

### Tool ID
- **Tool Name**: Google Search (Scale SERP)
- **Tool ID**: `65c51c556eb563350f6e1bb1`
- **Vendor**: Google (via Scale SERP)
- **Hosted on**: Google
- **Price**: $0.0008 per request

### Configuration in Code

The Google Search tool is configured in `api/config.py`:

```python
TOOL_IDS: Dict[str, str] = {
    "tavily_search": "6736411cf127849667606689",  # Tavily Search API
    "wikipedia": "6633fd59821ee31dd914e232",      # Wikipedia
    "google_search": "65c51c556eb563350f6e1bb1",   # Google Search (Scale SERP)
}
```

### Enabling/Disabling Google Search

Google Search is enabled by default in the Search Agent. To disable it:

```python
# In api/team_config.py
tools = TeamConfig.get_tools(include_google_search=False)
```

## Usage Strategy

### When to Use Google Search

The Search Agent is instructed to use Google Search as a fallback when:

1. **Tavily Search yields < 3 entities**: If the initial Tavily search doesn't find enough relevant entities
2. **German government topics**: For regional German topics like "Baden-Württemberg" policies
3. **Official sources**: When looking for government websites, ministries, official agencies
4. **Specific regional topics**: Topics with limited international coverage

### Search Strategy

The Search Agent follows this strategy:

1. **Start with Tavily Search**: Use Tavily as the primary tool (optimized for AI agents)
2. **Evaluate results**: Check if Tavily returned at least 3 entities
3. **Fallback to Google Search**: If < 3 entities, use Google Search with same or broader terms
4. **Combine results**: Merge entities from both tools for comprehensive coverage

### Tool Comparison

| Feature | Tavily Search | Google Search |
|---------|--------------|---------------|
| **Optimization** | AI-optimized | General web search |
| **Quality** | High-quality, curated results | Comprehensive coverage |
| **Best for** | Quick research, international topics | Government sites, official sources |
| **Coverage** | Focused, relevant results | Broad, exhaustive results |
| **Cost** | Higher per request | Lower per request ($0.0008) |

## Implementation Details

### Search Agent Instructions

The Search Agent includes these instructions for Google Search:

```
SEARCH STRATEGY:
1. Start with Tavily Search using specific search terms
2. For German government topics, search: "[topic] Baden-Württemberg site:.de"
3. For people, search: "[name] [role] Baden-Württemberg"
4. For organizations, search: "[organization name] [location]"
5. If Tavily Search yields < 3 entities, use Google Search as backup
6. Google Search can provide more comprehensive coverage

TOOL USAGE GUIDELINES:
- Tavily Search: Primary tool, optimized for AI agents
- Google Search: Backup tool when Tavily yields < 3 entities
- Use Google Search for: government websites, official sources, German regional topics
- Combine results from both tools for comprehensive coverage
```

### Code Example

```python
from api.team_config import TeamConfig

# Create team with Google Search enabled (default)
team = TeamConfig.create_team(
    topic="Jugendschutz Baden-Württemberg 2025",
    goals=["Find youth protection organizations"],
    model="testing"
)

# Run team - Search Agent will use Tavily first, then Google if needed
response = team.run(prompt)
```

## When Google Search Provides Better Results

Based on testing and analysis, Google Search provides better results for:

### 1. German Regional Topics
- **Example**: "Jugendschutz Baden-Württemberg 2025"
- **Why**: Google has better coverage of German government websites (.de domains)
- **Result**: More entities from state ministries, local agencies

### 2. Government and Official Sources
- **Example**: "Ministerium für Soziales Baden-Württemberg"
- **Why**: Google indexes government websites more comprehensively
- **Result**: Better coverage of official agencies, departments, programs

### 3. Specific Local Organizations
- **Example**: "Caritas Baden-Württemberg Kinderarmut"
- **Why**: Google finds regional NGO websites and local branches
- **Result**: More specific, localized entities

### 4. Historical or Archived Content
- **Example**: "Integration policies Baden-Württemberg 2015-2020"
- **Why**: Google has deeper historical archives
- **Result**: Better coverage of past policies, programs, officials

### 5. Topics with Limited International Coverage
- **Example**: "Landesanstalt für Umwelt Baden-Württemberg"
- **Why**: Tavily may prioritize international sources
- **Result**: Google finds more regional, German-language sources

## Testing

### Unit Tests

Run unit tests to verify configuration:

```bash
python -m pytest tests/test_google_search_integration.py -v -m "not integration"
```

Tests verify:
- ✓ Google Search tool ID is configured
- ✓ Search Agent instructions mention Google Search as backup

### Integration Tests

Run integration tests with real API calls:

```bash
python -m pytest tests/test_google_search_integration.py -v -m "integration"
```

Integration tests verify:
- ✓ Google Search tool can be retrieved from aixplain
- ✓ Search Agent is created with Google Search tool
- ✓ Team can execute with Google Search enabled
- ✓ Results include entities from both Tavily and Google

### Manual Testing

To manually test Google Search integration:

1. Start the API server:
   ```bash
   python api/main.py
   ```

2. Create a team with a German regional topic:
   ```bash
   curl -X POST http://localhost:8080/api/v1/agent-teams \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Jugendschutz Baden-Württemberg 2025",
       "goals": ["Find youth protection organizations"]
     }'
   ```

3. Monitor the execution logs to see when Google Search is used

4. Check the results for entities from German government sources

## Cost Considerations

### Google Search Pricing
- **Cost per request**: $0.0008
- **Typical usage**: 2-5 requests per topic (when used as fallback)
- **Cost per topic**: ~$0.002 - $0.004 additional cost

### When to Disable Google Search

Consider disabling Google Search if:
- Budget is very limited
- Topics are primarily international (Tavily sufficient)
- Speed is more important than comprehensive coverage
- Testing/development environment

To disable:
```python
tools = TeamConfig.get_tools(include_google_search=False)
```

## Troubleshooting

### Google Search Not Working

1. **Check tool ID**: Verify `65c51c556eb563350f6e1bb1` is correct
2. **Check API key**: Ensure aixplain API key has access to Google Search tool
3. **Check logs**: Look for "Failed to retrieve Google Search tool" errors
4. **Test tool directly**:
   ```python
   from aixplain.factories import ToolFactory
   tool = ToolFactory.get("65c51c556eb563350f6e1bb1")
   result = tool.run({"text": "test query"})
   ```

### Google Search Not Used as Fallback

1. **Check Tavily results**: If Tavily returns ≥3 entities, Google won't be used
2. **Check agent logs**: Look for "Using Google Search as backup" messages
3. **Verify instructions**: Ensure Search Agent instructions mention Google fallback

### Duplicate Entities

If you see duplicate entities from Tavily and Google:
- This is expected behavior - both tools may find the same entities
- Entity deduplication should handle this (see Task 20.4)
- Duplicates are merged based on name and type

## Future Enhancements

1. **Smart Tool Selection**: Use ML to predict which tool will work best for a topic
2. **Parallel Search**: Run Tavily and Google in parallel for faster results
3. **Cost Optimization**: Track which tool provides better ROI per topic type
4. **Regional Tool Selection**: Automatically prefer Google for German topics

## References

- [aixplain Google Search Tool](https://platform.aixplain.com/marketplace/tools/65c51c556eb563350f6e1bb1)
- [Scale SERP Documentation](https://www.scaleserp.com/docs)
- [Task 21: Add Google Search Tool](../.kiro/specs/osint-agent-team-system/tasks.md#task-21)
