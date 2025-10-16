# Design Document: LibreChat MCP Service

## Overview

This design describes an MCP (Model Context Protocol) server that exposes the existing OSINT agent team system to LibreChat. The MCP server will act as a bridge between LibreChat and the existing FastAPI backend, providing tools for spawning agent teams and retrieving historical execution data in JSON-LD format.

The design leverages the existing architecture where:
- FastAPI backend manages agent team lifecycle and storage
- Agent teams use aixplain's TeamAgentFactory with built-in micro agents (Mentalist, Inspector, Orchestrator, Response Generator)
- Entity extraction produces JSON-LD Sachstand output in schema.org format
- SQLite database persists all execution data

## Architecture

### High-Level Architecture

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

**Key Design Principle**: The MCP server is completely stateless and acts as a thin translation layer between the MCP protocol and the FastAPI REST API. All data persistence and business logic remains in the FastAPI backend.

### Component Interaction Flow

1. **Agent Team Spawning Flow** (Asynchronous):
   - LibreChat user invokes `spawn_agent_team` MCP tool
   - MCP server receives request with topic and optional parameters
   - MCP server calls FastAPI `/api/v1/agent-teams` endpoint
   - FastAPI creates team record and starts background task
   - MCP server immediately returns execution ID and status "pending"
   - Agent team runs in background (1-2 minutes typically)
   - LibreChat can poll status using `get_execution_status` tool

2. **Status Checking Flow**:
   - LibreChat user invokes `get_execution_status` MCP tool with execution ID
   - MCP server queries database for current status
   - Returns status: "pending", "running", "completed", or "failed"
   - If completed, includes entity count and completion time

3. **Results Retrieval Flow**:
   - LibreChat user invokes `get_execution_results` MCP tool with execution ID
   - MCP server checks if execution is completed
   - If completed, retrieves full JSON-LD Sachstand from database
   - Returns complete JSON-LD response to LibreChat
   - If not completed, returns error with current status

4. **Historical Data Listing Flow**:
   - LibreChat user invokes `list_executions` MCP tool
   - MCP server calls FastAPI `GET /api/v1/agent-teams` endpoint with query parameters
   - FastAPI queries database and returns filtered/paginated list
   - MCP server formats response as JSON-LD and returns to LibreChat

### Technology Stack

- **MCP Server**: Python with `mcp` library (FastMCP or similar)
- **Communication**: stdio transport for MCP protocol
- **Backend Integration**: HTTP requests to existing FastAPI server via `httpx`
- **Data Format**: JSON-LD with schema.org vocabulary
- **State Management**: Stateless - all data managed by FastAPI backend

## Components and Interfaces

### MCP Server Component

**Responsibilities**:
- Implement MCP protocol server
- Expose tools for agent team operations
- Translate MCP tool calls to FastAPI HTTP requests
- Format FastAPI responses as JSON-LD
- Handle errors and provide user-friendly messages

**Key Classes**:

```python
class LibreChatMCPServer:
    """Main MCP server for LibreChat integration (stateless)"""
    
    def __init__(self, api_base_url: str):
        """Initialize with FastAPI URL"""
        self.fastapi_client = FastAPIClient(api_base_url)
        
    async def spawn_agent_team(
        self, 
        topic: str, 
        goals: List[str] = None,
        interaction_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Spawn a new agent team for topic research.
        Calls FastAPI backend and returns immediately with execution ID.
        """
        
    async def get_execution_status(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get current status of an execution.
        Calls FastAPI backend to get team details.
        """
        
    async def get_execution_results(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get full JSON-LD results for a completed execution.
        Calls FastAPI backend to get sachstand.
        """
        
    async def list_executions(
        self,
        topic_filter: str = None,
        status_filter: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        List executions with filtering.
        Calls FastAPI backend list endpoint.
        """
```

### MCP Tools Interface

**Tool 1: spawn_agent_team**

```json
{
  "name": "spawn_agent_team",
  "description": "Spawn an OSINT agent team to research a topic. Returns immediately with execution ID. Use get_execution_status to check progress.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "topic": {
        "type": "string",
        "description": "Research topic (e.g., 'Kinderarmut in Deutschland')"
      },
      "goals": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional research goals"
      },
      "interaction_limit": {
        "type": "integer",
        "default": 50,
        "description": "Maximum agent interactions before returning results"
      }
    },
    "required": ["topic"]
  }
}
```

**Tool 2: get_execution_status**

```json
{
  "name": "get_execution_status",
  "description": "Check the status of a running or completed execution",
  "inputSchema": {
    "type": "object",
    "properties": {
      "execution_id": {
        "type": "string",
        "description": "Execution ID returned from spawn_agent_team"
      }
    },
    "required": ["execution_id"]
  }
}
```

**Tool 3: get_execution_results**

```json
{
  "name": "get_execution_results",
  "description": "Get full JSON-LD results for a completed execution. Returns error if not completed.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "execution_id": {
        "type": "string",
        "description": "Execution ID of completed execution"
      }
    },
    "required": ["execution_id"]
  }
}
```

**Tool 4: list_executions**

```json
{
  "name": "list_executions",
  "description": "List all executions with optional filtering and pagination",
  "inputSchema": {
    "type": "object",
    "properties": {
      "topic_filter": {
        "type": "string",
        "description": "Filter by topic substring (case-insensitive)"
      },
      "status_filter": {
        "type": "string",
        "enum": ["pending", "running", "completed", "failed"],
        "description": "Filter by execution status"
      },
      "limit": {
        "type": "integer",
        "default": 10,
        "description": "Maximum number of results (max 100)"
      },
      "offset": {
        "type": "integer",
        "default": 0,
        "description": "Offset for pagination"
      }
    }
  }
}
```

### FastAPI Integration Component

**Responsibilities**:
- Make HTTP requests to existing FastAPI endpoints
- Handle authentication if needed
- Parse responses and handle errors
- Provide async interface for all backend operations

**Key Methods**:

```python
class FastAPIClient:
    """Client for FastAPI backend"""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """Initialize with API base URL and timeout"""
        
    async def create_team(
        self,
        topic: str,
        goals: List[str],
        interaction_limit: int,
        mece_strategy: str = "depth_first"
    ) -> Dict[str, Any]:
        """POST /api/v1/agent-teams"""
        
    async def get_team_status(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """GET /api/v1/agent-teams/{team_id}"""
        
    async def get_sachstand(
        self,
        team_id: str
    ) -> Dict[str, Any]:
        """GET /api/v1/sachstand/{team_id}"""
        
    async def list_teams(
        self,
        topic_filter: str = None,
        status_filter: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """GET /api/v1/agent-teams with query parameters"""
```

**Note**: The `list_teams` method may require enhancing the FastAPI backend to support filtering by topic and status via query parameters.

### FastAPI Backend Enhancement (Optional)

To support filtering in the `list_executions` MCP tool, the FastAPI backend's `GET /api/v1/agent-teams` endpoint should be enhanced to accept query parameters:

```python
@app.get("/api/v1/agent-teams", response_model=list[AgentTeamSummary])
async def list_agent_teams(
    topic: Optional[str] = None,  # Filter by topic substring
    status: Optional[str] = None,  # Filter by status
    limit: int = 10,  # Pagination limit
    offset: int = 0   # Pagination offset
):
    """List agent teams with optional filtering and pagination"""
```

If this enhancement is not implemented, the MCP server can:
1. Fetch all teams from the backend
2. Apply filtering client-side
3. Return filtered results to LibreChat

This is acceptable for small datasets but less efficient for large numbers of executions.

## Data Models

### Spawn Response Model

```python
{
  "@context": "https://schema.org",
  "@type": "Action",
  "actionStatus": "PotentialActionStatus",
  "object": {
    "@type": "ResearchReport",
    "identifier": "team_id_uuid",
    "name": "Research topic",
    "dateCreated": "2025-10-15T10:30:00Z",
    "status": "pending"
  },
  "result": {
    "message": "Agent team spawned successfully. Use get_execution_status to check progress."
  }
}
```

### Status Response Model

```python
{
  "@context": "https://schema.org",
  "@type": "ResearchReport",
  "identifier": "team_id_uuid",
  "name": "Research topic",
  "dateCreated": "2025-10-15T10:30:00Z",
  "dateModified": "2025-10-15T10:35:00Z",
  "status": "completed",  # or "pending", "running", "failed"
  "numberOfEntities": 15,  # only if completed
  "duration": "PT5M23S"  # ISO 8601 duration, only if completed
}
```

### Execution List Model

```python
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "numberOfItems": 10,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "ResearchReport",
        "identifier": "team_id_uuid",
        "name": "Research topic",
        "dateCreated": "2025-10-15T10:30:00Z",
        "dateModified": "2025-10-15T10:35:00Z",
        "status": "completed",
        "numberOfEntities": 15
      }
    }
  ]
}
```

### Execution Details Model

The execution details will return the full JSON-LD Sachstand as stored in the database, which follows the existing schema:

```python
{
  "@context": "https://schema.org",
  "@type": "ResearchReport",
  "name": "Sachstand: [Topic]",
  "dateCreated": "2025-10-15T10:35:00Z",
  "about": {
    "@type": "Topic",
    "name": "[Topic]"
  },
  "hasPart": [
    {
      "@type": "Person",
      "name": "Person Name",
      "description": "Description",
      "jobTitle": "Job Title",
      "sources": [
        {
          "url": "https://example.com",
          "excerpt": "Relevant excerpt"
        }
      ],
      "sameAs": ["https://www.wikidata.org/wiki/Q123"],
      "wikidata_id": "Q123"
    },
    {
      "@type": "Organization",
      "name": "Organization Name",
      "description": "Description",
      "sources": [...]
    }
  ],
  "completionStatus": "complete"
}
```

### Error Response Model

```python
{
  "@context": "https://schema.org",
  "@type": "ErrorResponse",
  "error": {
    "code": "EXECUTION_NOT_FOUND",
    "message": "Execution with ID xyz not found",
    "timestamp": "2025-10-15T10:35:00Z"
  }
}
```

## Error Handling

### Error Categories

1. **MCP Protocol Errors**:
   - Invalid tool parameters
   - Missing required fields
   - Type validation failures

2. **Backend Communication Errors**:
   - FastAPI server unreachable
   - HTTP request timeouts
   - Authentication failures

3. **Database Errors**:
   - Database file not found
   - Query execution failures
   - Corrupted data

4. **Business Logic Errors**:
   - Execution not found
   - Execution not completed (when requesting results)
   - Invalid filter parameters

### Error Handling Strategy

```python
class MCPError(Exception):
    """Base MCP error"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

class ExecutionNotFoundError(MCPError):
    """Execution ID not found"""
    pass

class ExecutionNotCompletedError(MCPError):
    """Execution not yet completed"""
    pass

class BackendUnavailableError(MCPError):
    """FastAPI backend unavailable"""
    pass

# Error responses follow JSON-LD format
def format_error_response(error: MCPError) -> Dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "ErrorResponse",
        "error": {
            "code": error.code,
            "message": error.message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
```

## Configuration

### Environment Variables

```bash
# FastAPI Backend
FASTAPI_BASE_URL=http://localhost:8000

# MCP Server
MCP_SERVER_NAME=librechat-osint-mcp
MCP_SERVER_VERSION=0.1.0

# HTTP Client Configuration
HTTP_TIMEOUT=30.0  # Request timeout in seconds
```

### MCP Server Configuration File

LibreChat users will configure the MCP server in their `mcp.json`:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Testing Strategy

### Unit Tests

1. **MCP Tool Tests**:
   - Test tool parameter validation
   - Test tool response formatting
   - Test error handling

2. **FastAPI Client Tests**:
   - Mock HTTP requests
   - Test request formatting
   - Test response parsing
   - Test error handling

3. **Database Query Tests**:
   - Test query construction
   - Test filtering logic
   - Test pagination
   - Test data extraction

### Integration Tests

1. **End-to-End Flow Tests**:
   - Spawn agent team and retrieve results
   - Query historical data
   - Handle concurrent requests

2. **Error Scenario Tests**:
   - Backend unavailable
   - Database locked
   - Invalid execution IDs
   - Timeout scenarios

### Manual Testing

1. **LibreChat Integration**:
   - Configure MCP server in LibreChat
   - Test tool discovery
   - Test tool invocation from chat
   - Verify JSON-LD response rendering

## Performance Considerations

### Asynchronous Execution

- All agent team spawning is asynchronous
- MCP tools return immediately (< 100ms response time)
- No connection held open during agent execution
- LibreChat polls status as needed using `get_execution_status`

### Response Caching (Optional)

Since the MCP server is stateless, caching can be implemented if needed:
- Cache completed execution results for a short duration (e.g., 5 minutes)
- Use in-memory LRU cache to reduce FastAPI backend load
- Cache key: execution_id
- Invalidation: Time-based expiry only (no manual invalidation needed)

## Security Considerations

### Authentication

- MCP server runs locally, no authentication needed
- FastAPI backend may require API key in the future (pass via environment)
- All requests proxied through FastAPI backend (no direct database access)

### Data Privacy

- No PII filtering at MCP layer (handled by agents)
- All data stored locally
- No external data transmission except to FastAPI backend

### Input Validation

- Validate all tool parameters against schema
- Sanitize topic strings to prevent injection
- Limit query result sizes to prevent DoS

## Deployment

### Installation

```bash
# Install MCP server package
pip install -e ./mcp_server

# Or use uvx for isolated execution
uvx librechat-osint-mcp-server
```

### Running the Server

```bash
# Standalone mode (for testing)
python -m mcp_server.main

# Via LibreChat (configured in mcp.json)
# LibreChat will spawn the server automatically
```

### Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.10"
mcp = "^0.9.0"  # MCP SDK
httpx = "^0.27.0"  # Async HTTP client
pydantic = "^2.0.0"  # Data validation (optional, for type safety)
```

## Future Enhancements

1. **Streaming Support**:
   - Stream agent execution logs in real-time
   - Use MCP streaming protocol for progress updates

2. **Advanced Filtering**:
   - Full-text search on topics
   - Date range filtering
   - Entity type filtering

3. **Execution Management**:
   - Cancel running executions
   - Retry failed executions
   - Clone execution with modified parameters

4. **Analytics**:
   - Execution statistics
   - Entity extraction metrics
   - Performance trends

5. **Multi-Backend Support**:
   - Support multiple FastAPI instances
   - Load balancing across backends
   - Failover handling
