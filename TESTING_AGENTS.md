# Testing Agents Standalone

This guide explains how to test agents outside the team context for debugging.

## Quick Start

### 1. Test Tavily Tool Access

First, verify the Tavily tool is accessible:

```bash
poetry run python test_tavily_tool.py
```

This will:
- Check environment variables (AIXPLAIN_API_KEY, TAVILY_API_KEY)
- Verify tool configuration
- Test tool access and execution
- Run a simple search query

**Expected Output:**
```
✓ AIXPLAIN_API_KEY: b2ee282cca...813e
✓ TAVILY_API_KEY: tvly-xxxxx...xxxx
✓ Tavily Tool ID: 123456789
✓ Tool fetched successfully
✓ Tool executed successfully
✓ ALL TESTS PASSED
```

### 2. Test Search Agent Standalone

Test the Search Agent without team overhead:

```bash
# Test with default topic (Angela Merkel)
poetry run python test_agent_standalone.py

# Test with custom topic
poetry run python test_agent_standalone.py "Familienforum Markdorf"

# Verbose mode (shows prompts and full traces)
poetry run python test_agent_standalone.py "United Nations" --verbose
```

**What it does:**
- Creates the Search Agent with Tavily tool
- Runs a research query
- Shows agent output and execution stats
- Saves full response to JSON file
- Detects errors in output

**Expected Output:**
```
STANDALONE AGENT TEST
Topic: Angela Merkel
Model: GPT-4o
✓ Search Agent created: Search Agent
  Agent ID: 68f1372b56dba95043001c7e
  Tools: ['Tavily Search']

AGENT RESPONSE
Output:
[Agent's research results with entities]

Execution Stats:
  runtime: 15.2
  credits: 0.05
  api_calls: 3

✓ Full response saved to: test_agent_output_Angela_Merkel.json
TEST COMPLETED
```

## Troubleshooting

### Error: "An error occurred during execution"

This generic error from aixplain can mean:

1. **Tavily API Key Invalid**
   ```bash
   # Check your .env file
   grep TAVILY_API_KEY .env
   
   # Test Tavily directly
   poetry run python test_tavily_tool.py
   ```

2. **Tool Not Configured**
   ```bash
   # Check api/config.py has:
   TOOL_IDS = {
       "tavily_search": "your_tool_id_here"
   }
   ```

3. **aixplain API Key Issues**
   ```bash
   # Verify key has permissions
   grep AIXPLAIN_API_KEY .env
   ```

### Error: "Tool not accessible"

Run the Tavily tool test:
```bash
poetry run python test_tavily_tool.py
```

If it fails, check:
- Tavily API key is valid
- Tool ID is correct in `api/config.py`
- Network connectivity

### Agent Returns Empty Results

Try a well-known topic first:
```bash
poetry run python test_agent_standalone.py "Barack Obama"
```

If this works but your topic doesn't, the topic might be:
- Too specific or niche
- Not well-documented online
- Spelled incorrectly

## Output Files

Test scripts create output files:

- `test_agent_output_<topic>.json` - Full agent response
- Contains raw response data for debugging

## Comparing with Team Execution

**Standalone Agent:**
- Direct agent execution
- No team coordination overhead
- Faster, simpler
- Good for debugging tool/agent issues

**Team Execution:**
- Mentalist plans strategy
- Orchestrator coordinates
- Inspector reviews
- Response Generator formats
- More complex, slower
- Better for comprehensive research

## Next Steps

If standalone tests pass but team execution fails:
1. Check team configuration in `api/team_config.py`
2. Review team logs in web UI
3. Download complete debug data from team detail page
4. Compare standalone output with team output

## Environment Variables Required

```bash
# .env file
AIXPLAIN_API_KEY=your_aixplain_key
TAVILY_API_KEY=your_tavily_key
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "TAVILY_API_KEY not set" | Add to .env file |
| "Tool ID not configured" | Update api/config.py |
| "Permission denied" | Check aixplain API key permissions |
| "Network error" | Check internet connection |
| "Tool not found" | Verify tool ID is correct |

## Getting Help

1. Run `poetry run python test_tavily_tool.py` first
2. If that passes, run `poetry run python test_agent_standalone.py`
3. Check output files for detailed error messages
4. Review server logs in web UI for team executions
5. Download complete debug data from team detail page
