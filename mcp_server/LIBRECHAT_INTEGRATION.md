# LibreChat Integration Guide

This guide explains how to integrate the OSINT Agent Team MCP server with LibreChat and test the integration.

## Overview

The MCP server exposes four tools to LibreChat:
1. **spawn_agent_team** - Start a new OSINT research task
2. **get_execution_status** - Check the status of a running task
3. **get_execution_results** - Retrieve results from a completed task
4. **list_executions** - List all past executions with filtering

## Prerequisites

### 1. LibreChat Installation

Install LibreChat following the official documentation:
- https://docs.librechat.ai/install/installation/index.html

### 2. MCP Server Setup

Ensure the MCP server is installed:

```bash
cd mcp_server
poetry install
```

### 3. FastAPI Backend Running

The MCP server requires the FastAPI backend to be running:

```bash
# From project root
./start-backend.sh
```

## Configuration

### Step 1: Configure MCP Server in LibreChat

Create or edit the MCP configuration file for LibreChat. The location depends on your LibreChat installation:

**For Docker installations:**
```bash
# Edit docker-compose.yml to mount the config
volumes:
  - ./librechat.yaml:/app/librechat.yaml
  - ./mcp.json:/app/mcp.json
```

**For local installations:**
```bash
# Create mcp.json in LibreChat root directory
touch mcp.json
```

### Step 2: Add MCP Server Configuration

Edit `mcp.json` and add the OSINT Agent Team MCP server:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/agentic-researcher-team-aixplain/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Replace `/path/to/agentic-researcher-team-aixplain/mcp_server` with the actual path to your MCP server directory.

### Step 3: Alternative Configuration (Using Poetry)

If you want to use Poetry to run the MCP server:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "poetry",
      "args": ["run", "python", "-m", "mcp_server.main"],
      "cwd": "/path/to/agentic-researcher-team-aixplain/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Step 4: Configuration for Remote Backend

If your FastAPI backend is running on a different machine:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/agentic-researcher-team-aixplain/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://your-backend-host:8000",
        "HTTP_TIMEOUT": "60.0",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Testing the Integration

### Manual Testing Steps

#### 1. Start LibreChat

```bash
# For Docker
docker-compose up -d

# For local installation
npm start
```

#### 2. Verify Tool Discovery

Open LibreChat in your browser and:
1. Start a new conversation
2. Look for the tools icon or MCP tools menu
3. Verify that the following tools are available:
   - spawn_agent_team
   - get_execution_status
   - get_execution_results
   - list_executions

#### 3. Test Spawning an Agent Team

In the LibreChat chat interface, try:

```
Use the spawn_agent_team tool to research "Kinderarmut in Deutschland"
```

Expected response:
- JSON-LD formatted response with execution ID
- Status: "pending"
- Message indicating the team was spawned successfully

#### 4. Test Checking Status

After spawning a team, check its status:

```
Use the get_execution_status tool to check the status of execution [execution_id]
```

Replace `[execution_id]` with the ID from step 3.

Expected response:
- Status: "pending", "running", or "completed"
- If completed: entity count and duration

#### 5. Test Retrieving Results

Once the execution is completed:

```
Use the get_execution_results tool to get the results for execution [execution_id]
```

Expected response:
- Full JSON-LD Sachstand document
- List of entities with descriptions and sources
- Wikidata IDs where available

#### 6. Test Listing Executions

List all past executions:

```
Use the list_executions tool to show all past research tasks
```

Expected response:
- JSON-LD ItemList with all executions
- Each item includes: ID, topic, status, date

#### 7. Test Filtering

Test filtering by topic:

```
Use the list_executions tool to find all executions about "Kinderarmut"
```

Test filtering by status:

```
Use the list_executions tool to show only completed executions
```

### Automated Testing Checklist

Use this checklist to verify all functionality:

- [ ] **Tool Discovery**
  - [ ] All 4 tools are visible in LibreChat
  - [ ] Tool descriptions are clear and helpful
  - [ ] Tool parameters are correctly defined

- [ ] **spawn_agent_team Tool**
  - [ ] Can spawn with topic only
  - [ ] Can spawn with topic and goals
  - [ ] Can spawn with custom interaction_limit
  - [ ] Returns valid JSON-LD response
  - [ ] Returns unique execution ID
  - [ ] Handles empty topic error
  - [ ] Handles invalid interaction_limit error

- [ ] **get_execution_status Tool**
  - [ ] Returns status for existing execution
  - [ ] Shows "pending" status immediately after spawn
  - [ ] Shows "running" status during execution
  - [ ] Shows "completed" status with entity count
  - [ ] Handles non-existent execution ID error
  - [ ] Handles empty execution_id error

- [ ] **get_execution_results Tool**
  - [ ] Returns full JSON-LD results for completed execution
  - [ ] Returns error for non-completed execution
  - [ ] Returns error for non-existent execution
  - [ ] Results include all entities with sources
  - [ ] Results include Wikidata IDs where available
  - [ ] Handles empty execution_id error

- [ ] **list_executions Tool**
  - [ ] Lists all executions
  - [ ] Filters by topic (substring match)
  - [ ] Filters by status (pending/running/completed/failed)
  - [ ] Supports pagination (limit/offset)
  - [ ] Returns empty list when no matches
  - [ ] Handles invalid status_filter error
  - [ ] Handles invalid limit/offset errors

- [ ] **JSON-LD Format**
  - [ ] All responses include @context
  - [ ] All responses include @type
  - [ ] Entities follow schema.org vocabulary
  - [ ] Error responses follow JSON-LD format

- [ ] **Error Handling**
  - [ ] Backend unavailable error is clear
  - [ ] Timeout errors are handled gracefully
  - [ ] Parameter validation errors are helpful
  - [ ] HTTP errors are properly formatted

- [ ] **Performance**
  - [ ] Tool responses are fast (< 1s for status/list)
  - [ ] Spawning returns immediately (< 1s)
  - [ ] Results retrieval is fast (< 2s)
  - [ ] Concurrent requests work correctly

## Troubleshooting

### Tools Not Appearing in LibreChat

**Symptoms**: MCP tools are not visible in LibreChat interface

**Solutions**:
1. Check LibreChat logs for MCP server connection errors
2. Verify `mcp.json` path is correct
3. Verify `cwd` path in configuration is correct
4. Check that Python is in PATH
5. Restart LibreChat after configuration changes

```bash
# Check LibreChat logs
docker-compose logs -f  # For Docker
npm run logs            # For local installation
```

### MCP Server Not Starting

**Symptoms**: LibreChat shows "MCP server failed to start"

**Solutions**:
1. Test MCP server manually:
```bash
cd /path/to/mcp_server
python -m mcp_server.main
```

2. Check environment variables:
```bash
echo $FASTAPI_BASE_URL
```

3. Verify dependencies are installed:
```bash
poetry install
poetry run python -m mcp_server.main
```

### Backend Connection Errors

**Symptoms**: Tools return "Backend unavailable" errors

**Solutions**:
1. Verify FastAPI backend is running:
```bash
curl http://localhost:8000/health
```

2. Check FASTAPI_BASE_URL in mcp.json
3. Check firewall/network settings
4. Verify backend logs for errors

### Tool Execution Errors

**Symptoms**: Tools return errors when invoked

**Solutions**:
1. Check MCP server logs (set LOG_LEVEL=DEBUG)
2. Verify parameter formats match tool schemas
3. Test tools directly using example scripts:
```bash
cd mcp_server
python examples/01_spawn_agent_team.py
```

### Results Not Available

**Symptoms**: get_execution_results returns "not completed" error

**Solutions**:
1. Check execution status first:
```bash
python examples/02_check_status.py [execution_id]
```

2. Wait for execution to complete (typically 1-2 minutes)
3. Check backend logs for execution errors
4. Verify agent team completed successfully

## Example Conversations

### Example 1: Basic Research Task

**User**: Research "Climate Change Policy in Germany"

**Assistant**: I'll use the spawn_agent_team tool to start researching this topic.

[Tool call: spawn_agent_team with topic="Climate Change Policy in Germany"]

**Tool Response**:
```json
{
  "@context": "https://schema.org",
  "@type": "Action",
  "actionStatus": "PotentialActionStatus",
  "object": {
    "@type": "ResearchReport",
    "identifier": "abc123",
    "name": "Climate Change Policy in Germany",
    "status": "pending"
  }
}
```

**Assistant**: I've started researching "Climate Change Policy in Germany". The execution ID is abc123. This typically takes 1-2 minutes. Would you like me to check the status?

**User**: Yes, check the status

[Tool call: get_execution_status with execution_id="abc123"]

**Tool Response**: [Status response showing "running" or "completed"]

### Example 2: Retrieving Past Research

**User**: Show me all my past research tasks

**Assistant**: I'll list all your past executions.

[Tool call: list_executions]

**Tool Response**: [ItemList with all executions]

**Assistant**: Here are your past research tasks: [formatted list]

**User**: Get the results for the one about climate change

[Tool call: get_execution_results with execution_id="abc123"]

**Tool Response**: [Full JSON-LD Sachstand]

**Assistant**: Here are the results: [formatted entity list with sources]

## Advanced Configuration

### Custom Timeout

For slower backends or complex research tasks:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "HTTP_TIMEOUT": "120.0"
      }
    }
  }
}
```

### Debug Logging

Enable debug logging to troubleshoot issues:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

Logs will be written to LibreChat's MCP server logs.

### Multiple Backends

Configure multiple MCP servers for different backends:

```json
{
  "mcpServers": {
    "osint-agent-teams-dev": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    },
    "osint-agent-teams-prod": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "https://prod-backend.example.com"
      }
    }
  }
}
```

## Security Considerations

### Local Deployment

For local development:
- MCP server runs locally with no authentication
- Backend should only be accessible from localhost
- No sensitive data should be exposed

### Production Deployment

For production use:
- Use HTTPS for backend communication
- Implement API key authentication in FastAPI backend
- Pass API key via environment variable:

```json
{
  "env": {
    "FASTAPI_BASE_URL": "https://backend.example.com",
    "FASTAPI_API_KEY": "your-api-key-here"
  }
}
```

- Restrict network access to backend
- Use secure credential storage for API keys

## Performance Optimization

### Caching

The MCP server is stateless and doesn't cache responses. To improve performance:

1. **Backend caching**: Implement caching in FastAPI backend
2. **LibreChat caching**: LibreChat may cache tool responses
3. **Database indexing**: Ensure database has proper indexes

### Concurrent Requests

The MCP server supports concurrent requests:
- Multiple users can spawn teams simultaneously
- Status checks don't block other operations
- Results retrieval is independent per execution

### Resource Limits

Configure resource limits in LibreChat:
- Max concurrent tool calls
- Tool execution timeout
- Response size limits

## Related Documentation

- [MCP Server README](README.md)
- [E2E Integration Tests](tests/README_E2E.md)
- [Example Scripts](examples/README.md)
- [LibreChat MCP Documentation](https://docs.librechat.ai/features/mcp.html)
