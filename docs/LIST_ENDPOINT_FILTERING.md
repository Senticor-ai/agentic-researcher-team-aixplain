# List Endpoint Filtering and Pagination

## Overview

The `/api/v1/agent-teams` endpoint now supports server-side filtering and pagination through query parameters. This enhancement improves performance and usability when working with large numbers of agent team executions.

## Endpoint

```
GET /api/v1/agent-teams
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | string | None | Filter by topic substring (case-insensitive) |
| `status` | string | None | Filter by exact status match (`pending`, `running`, `completed`, `failed`) |
| `limit` | integer | 10 | Maximum number of results to return (max: 100) |
| `offset` | integer | 0 | Number of results to skip for pagination |

## Examples

### List all teams (default limit of 10)
```bash
curl "http://localhost:8000/api/v1/agent-teams"
```

### Filter by topic
```bash
# Find all teams researching "Kinderarmut"
curl "http://localhost:8000/api/v1/agent-teams?topic=Kinderarmut"

# Case-insensitive: also matches "kinderarmut", "KINDERARMUT", etc.
curl "http://localhost:8000/api/v1/agent-teams?topic=kinder"
```

### Filter by status
```bash
# Get all completed teams
curl "http://localhost:8000/api/v1/agent-teams?status=completed"

# Get all running teams
curl "http://localhost:8000/api/v1/agent-teams?status=running"
```

### Combined filters
```bash
# Get completed teams about "armut"
curl "http://localhost:8000/api/v1/agent-teams?topic=armut&status=completed"
```

### Pagination
```bash
# Get first 5 teams
curl "http://localhost:8000/api/v1/agent-teams?limit=5&offset=0"

# Get next 5 teams
curl "http://localhost:8000/api/v1/agent-teams?limit=5&offset=5"

# Get 20 teams (custom page size)
curl "http://localhost:8000/api/v1/agent-teams?limit=20"
```

### Combined filtering and pagination
```bash
# Get first 10 completed teams about "policy"
curl "http://localhost:8000/api/v1/agent-teams?topic=policy&status=completed&limit=10&offset=0"
```

## Response Format

The endpoint returns a JSON array of team summaries:

```json
[
  {
    "team_id": "uuid-here",
    "topic": "Kinderarmut in Deutschland",
    "status": "completed",
    "created_at": "2025-10-16T10:30:00Z",
    "updated_at": "2025-10-16T10:35:00Z",
    "entity_count": 15,
    "sachstand": { ... }
  },
  ...
]
```

## Implementation Details

### Database Layer

The filtering is implemented at the database level using SQL queries with parameterized filters:

```python
# In api/persistent_storage.py
def get_teams_filtered(
    self, 
    topic: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """Get teams with optional filtering and pagination"""
    # SQL query with WHERE clauses for filtering
    # LIKE operator for case-insensitive topic matching
    # Exact match for status
    # LIMIT and OFFSET for pagination
```

### API Layer

The FastAPI endpoint validates and enforces constraints:

```python
# In api/main.py
@app.get("/api/v1/agent-teams", response_model=list[AgentTeamSummary])
async def list_agent_teams(
    topic: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    # Enforce maximum limit of 100
    limit = min(limit, 100)
    
    # Call storage layer with filters
    teams = store.get_teams_filtered(
        topic=topic,
        status=status,
        limit=limit,
        offset=offset
    )
```

### MCP Client

The MCP server's FastAPI client automatically uses the query parameters:

```python
# In mcp_server/fastapi_client.py
async def list_teams(
    self,
    topic_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    # Passes filters as query parameters
    # Falls back to client-side filtering if backend doesn't support it
```

## Performance Considerations

- **Server-side filtering**: Reduces data transfer and processing on the client side
- **Database indexing**: The `created_at` column is used for ordering (consider adding an index for large datasets)
- **Limit enforcement**: Maximum limit of 100 prevents excessive data transfer
- **Case-insensitive search**: Uses SQL `LOWER()` function for topic matching

## Testing

Unit tests are available in `tests/test_list_endpoint_filtering.py`:

```bash
# Run the tests
python -m pytest tests/test_list_endpoint_filtering.py -v
```

Tests cover:
- Filtering by topic (case-insensitive)
- Filtering by status
- Combined filters
- Pagination (limit and offset)
- Empty results
- Ordering (newest first)

## Migration Notes

This enhancement is **backward compatible**:
- Existing clients that don't use query parameters will continue to work
- Default behavior returns the 10 most recent teams
- The MCP client has fallback logic for client-side filtering

## Future Enhancements

Potential improvements:
- Full-text search on topics
- Date range filtering (created_at, updated_at)
- Sorting options (by topic, status, entity_count)
- Response metadata (total count, has_more flag)
- Cursor-based pagination for better performance
