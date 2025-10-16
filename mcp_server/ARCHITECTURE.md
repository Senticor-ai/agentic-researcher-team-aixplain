# MCP Server Architecture

## Design Principle: Stateless Bridge

The MCP server is designed as a **completely stateless** bridge between LibreChat and the existing FastAPI backend. It has no database, no persistence layer, and no business logic - it simply translates MCP protocol calls into HTTP requests to the FastAPI backend.

## Architecture Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│  LibreChat  │ ◄─MCP──►│  MCP Server  │ ◄─HTTP─►│  FastAPI Backend│
└─────────────┘         └──────────────┘         └─────────────────┘
                           (Stateless)                    │
                                                          ▼
                                                  ┌──────────────┐
                                                  │   SQLite DB  │
                                                  └──────────────┘
```

## Component Responsibilities

### MCP Server (This Project)
- **Role**: Protocol translator
- **Responsibilities**:
  - Expose MCP tools to LibreChat
  - Translate MCP tool calls to HTTP requests
  - Format FastAPI responses as JSON-LD
  - Handle errors gracefully
- **State**: None - completely stateless
- **Dependencies**: FastAPI backend via HTTP

### FastAPI Backend (Existing)
- **Role**: Business logic and data persistence
- **Responsibilities**:
  - Manage agent team lifecycle
  - Execute OSINT research tasks
  - Store all execution data in SQLite
  - Serve REST API endpoints
  - Serve UI frontend
- **State**: All application state (teams, executions, results)
- **Endpoints Used by MCP**:
  - `POST /api/v1/agent-teams` - Create new team
  - `GET /api/v1/agent-teams/{team_id}` - Get team status
  - `GET /api/v1/agent-teams` - List all teams
  - `GET /api/v1/sachstand/{team_id}` - Get JSON-LD results

## Data Flow Examples

### 1. Spawn Agent Team
```
LibreChat → spawn_agent_team(topic="AI Safety")
  ↓
MCP Server → POST /api/v1/agent-teams {topic: "AI Safety", goals: [...]}
  ↓
FastAPI Backend → Creates team, starts background task, returns team_id
  ↓
MCP Server → Formats as JSON-LD Action response
  ↓
LibreChat ← Receives execution_id and status "pending"
```

### 2. Check Status
```
LibreChat → get_execution_status(execution_id="abc-123")
  ↓
MCP Server → GET /api/v1/agent-teams/abc-123
  ↓
FastAPI Backend → Queries database, returns team details
  ↓
MCP Server → Formats as JSON-LD ResearchReport with status
  ↓
LibreChat ← Receives status, entity_count, duration
```

### 3. Get Results
```
LibreChat → get_execution_results(execution_id="abc-123")
  ↓
MCP Server → GET /api/v1/sachstand/abc-123
  ↓
FastAPI Backend → Retrieves JSON-LD sachstand from database
  ↓
MCP Server → Returns JSON-LD as-is (already in correct format)
  ↓
LibreChat ← Receives full JSON-LD ResearchReport with entities
```

### 4. List Executions
```
LibreChat → list_executions(status_filter="completed")
  ↓
MCP Server → GET /api/v1/agent-teams
  ↓
MCP Server → Filters results client-side by status
  ↓
MCP Server → Formats as JSON-LD ItemList
  ↓
LibreChat ← Receives list of executions
```

## Why Stateless?

### Benefits
1. **Simplicity**: No database schema, migrations, or data consistency issues
2. **Reliability**: No state to corrupt or lose
3. **Scalability**: Can run multiple MCP server instances
4. **Maintainability**: Single source of truth (FastAPI backend)
5. **Separation of Concerns**: MCP server only handles protocol translation

### Trade-offs
- **Network Dependency**: Every request requires HTTP call to backend
- **Client-Side Filtering**: List filtering done in MCP server (acceptable for MVP)
- **No Caching**: Each request hits backend (can add optional caching later)

## Future Enhancements

### Optional Backend Enhancement
To improve list filtering performance, the FastAPI backend could be enhanced:

```python
@app.get("/api/v1/agent-teams")
async def list_agent_teams(
    topic: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    # Server-side filtering and pagination
```

This is **optional** - client-side filtering is acceptable for MVP.

### Optional MCP Caching
If backend load becomes an issue, add simple caching:
- Cache completed execution results for 5 minutes
- Use in-memory LRU cache
- No invalidation needed (time-based expiry only)

## Configuration

The MCP server requires only one configuration variable:

```bash
FASTAPI_BASE_URL=http://localhost:8000
```

Everything else is handled by the FastAPI backend.

## Testing Strategy

### Unit Tests
- Test FastAPIClient HTTP calls (mocked)
- Test JSON-LD formatters
- Test error handling

### Integration Tests
- Test with real FastAPI backend
- Test full workflow: spawn → status → results
- Test error scenarios (backend down, 404s, etc.)

### LibreChat Integration
- Configure in LibreChat's mcp.json
- Test tool discovery
- Test tool invocation from chat
- Verify JSON-LD rendering

## Summary

The MCP server is a **thin, stateless translation layer** that:
- ✅ Exposes MCP tools to LibreChat
- ✅ Proxies all requests to FastAPI backend
- ✅ Formats responses as JSON-LD
- ❌ Has no database or persistence
- ❌ Has no business logic
- ❌ Has no state

This design keeps the MCP server simple, reliable, and maintainable while leveraging the existing FastAPI backend for all data and business logic.
