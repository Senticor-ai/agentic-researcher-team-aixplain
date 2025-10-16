# LibreChat OSINT MCP Server

A Model Context Protocol (MCP) server that enables LibreChat to interact with the OSINT agent team system. This server provides tools for spawning agent teams to research topics and retrieving historical execution data, all in JSON-LD format for semantic interoperability.

## Features

- **Spawn Agent Teams**: Create OSINT research teams for any topic
- **Check Execution Status**: Monitor progress of running agent teams
- **Retrieve Results**: Get complete JSON-LD formatted research reports
- **List Executions**: Browse and filter historical research runs
- **Stateless Design**: All state managed by FastAPI backend
- **JSON-LD Output**: Semantic web-compatible structured data

## Architecture

The MCP server acts as a thin translation layer between LibreChat and the FastAPI backend:

```
LibreChat ◄─MCP─► MCP Server ◄─HTTP─► FastAPI Backend ◄─► SQLite DB
```

All business logic and data persistence is handled by the existing FastAPI backend. The MCP server is completely stateless.

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)
- Running FastAPI backend (see main project README)

### Install Dependencies

```bash
cd mcp_server
poetry install
```

### Alternative: Install with pip

```bash
cd mcp_server
pip install -e .
```

## Configuration

The MCP server is configured via environment variables. You can set these in your shell or in a `.env` file.

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FASTAPI_BASE_URL` | Base URL for the FastAPI backend | `http://localhost:8080` | Yes |
| `HTTP_TIMEOUT` | HTTP request timeout in seconds | `30.0` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` | No |
| `MCP_SERVER_NAME` | MCP server name | `librechat-osint-mcp` | No |
| `MCP_SERVER_VERSION` | MCP server version | `0.1.0` | No |

### Example .env File

Create a `.env` file in the `mcp_server` directory:

```bash
# FastAPI Backend
FASTAPI_BASE_URL=http://localhost:8080

# HTTP Client Configuration
HTTP_TIMEOUT=30.0

# Logging
LOG_LEVEL=INFO
```

## Usage

### Running Standalone (for testing)

```bash
# Using poetry
poetry run python -m mcp_server.main

# Or using python directly
python -m mcp_server.main
```

### LibreChat Integration

Add the MCP server to your LibreChat configuration file (`mcp.json`):

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note**: Make sure the FastAPI backend is running before starting LibreChat.

### Alternative: Using Poetry in LibreChat

If you installed with Poetry, you can use:

```json
{
  "mcpServers": {
    "osint-agent-teams": {
      "command": "poetry",
      "args": ["run", "python", "-m", "mcp_server.main"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "FASTAPI_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Available Tools

The MCP server exposes four tools that can be invoked from LibreChat:

### 1. spawn_agent_team

Spawn an OSINT agent team to research a topic. Returns immediately with an execution ID.

**Parameters:**
- `topic` (string, required): Research topic (e.g., "Kinderarmut in Deutschland")
- `goals` (array of strings, optional): Specific research goals
- `interaction_limit` (integer, optional): Maximum agent interactions (default: 50)

**Example:**
```json
{
  "topic": "Climate policy in Germany",
  "goals": ["Identify key stakeholders", "Find recent legislation"],
  "interaction_limit": 50
}
```

**Response:**
```json
{
  "@context": "https://schema.org",
  "@type": "Action",
  "actionStatus": "PotentialActionStatus",
  "object": {
    "@type": "ResearchReport",
    "identifier": "abc123-def456-...",
    "name": "Climate policy in Germany",
    "dateCreated": "2025-10-16T10:30:00Z",
    "status": "pending"
  },
  "result": {
    "message": "Agent team spawned successfully. Use get_execution_status to check progress."
  }
}
```

### 2. get_execution_status

Check the status of a running or completed execution.

**Parameters:**
- `execution_id` (string, required): Execution ID returned from spawn_agent_team

**Example:**
```json
{
  "execution_id": "abc123-def456-..."
}
```

**Response:**
```json
{
  "@context": "https://schema.org",
  "@type": "ResearchReport",
  "identifier": "abc123-def456-...",
  "name": "Climate policy in Germany",
  "dateCreated": "2025-10-16T10:30:00Z",
  "dateModified": "2025-10-16T10:35:00Z",
  "status": "completed",
  "numberOfEntities": 15,
  "duration": "PT5M23S"
}
```

**Status Values:**
- `pending`: Team created, not yet started
- `running`: Team is actively researching
- `completed`: Research finished successfully
- `failed`: Execution encountered an error

### 3. get_execution_results

Get full JSON-LD results for a completed execution. Returns an error if the execution is not yet completed.

**Parameters:**
- `execution_id` (string, required): Execution ID of completed execution

**Example:**
```json
{
  "execution_id": "abc123-def456-..."
}
```

**Response:**
```json
{
  "@context": "https://schema.org",
  "@type": "ResearchReport",
  "name": "Sachstand: Climate policy in Germany",
  "dateCreated": "2025-10-16T10:35:00Z",
  "about": {
    "@type": "Topic",
    "name": "Climate policy in Germany"
  },
  "hasPart": [
    {
      "@type": "Person",
      "name": "Dr. Jane Smith",
      "description": "Climate policy expert",
      "jobTitle": "Director of Climate Research",
      "sources": [
        {
          "url": "https://example.com/article",
          "excerpt": "Dr. Smith leads climate initiatives..."
        }
      ],
      "sameAs": ["https://www.wikidata.org/wiki/Q123"],
      "wikidata_id": "Q123"
    },
    {
      "@type": "Organization",
      "name": "Climate Action Network",
      "description": "Environmental advocacy organization",
      "sources": [...]
    }
  ],
  "completionStatus": "complete"
}
```

### 4. list_executions

List all executions with optional filtering and pagination.

**Parameters:**
- `topic_filter` (string, optional): Filter by topic substring (case-insensitive)
- `status_filter` (string, optional): Filter by status (pending, running, completed, failed)
- `limit` (integer, optional): Maximum results to return (default: 10, max: 100)
- `offset` (integer, optional): Offset for pagination (default: 0)

**Example:**
```json
{
  "topic_filter": "climate",
  "status_filter": "completed",
  "limit": 5
}
```

**Response:**
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "numberOfItems": 5,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "ResearchReport",
        "identifier": "abc123-def456-...",
        "name": "Climate policy in Germany",
        "dateCreated": "2025-10-16T10:30:00Z",
        "dateModified": "2025-10-16T10:35:00Z",
        "status": "completed",
        "numberOfEntities": 15
      }
    }
  ]
}
```

## Typical Workflow

1. **Spawn a team**: Use `spawn_agent_team` with your research topic
2. **Check status**: Poll `get_execution_status` until status is "completed" (typically 1-2 minutes)
3. **Get results**: Use `get_execution_results` to retrieve the full JSON-LD report
4. **Browse history**: Use `list_executions` to find past research runs

## Error Handling

All errors are returned in JSON-LD format:

```json
{
  "@context": "https://schema.org",
  "@type": "ErrorResponse",
  "error": {
    "code": "EXECUTION_NOT_FOUND",
    "message": "Execution with ID xyz not found",
    "timestamp": "2025-10-16T10:35:00Z"
  }
}
```

**Common Error Codes:**
- `INVALID_PARAMETER`: Invalid or missing parameter
- `EXECUTION_NOT_FOUND`: Execution ID does not exist
- `EXECUTION_NOT_COMPLETED`: Results requested for incomplete execution
- `BACKEND_ERROR`: FastAPI backend communication error
- `INTERNAL_ERROR`: Unexpected server error

## Logging

Logs are written to stderr (to avoid interfering with stdio transport) and include:
- Tool invocations and parameters
- HTTP requests to FastAPI backend
- Execution status changes
- Errors with stack traces

Set `LOG_LEVEL=DEBUG` for detailed debugging information.

## Examples

The `examples/` directory contains scripts demonstrating how to use the MCP server:

- `00_full_workflow.py` - Complete workflow from spawn to results
- `01_spawn_agent_team.py` - Spawn a new agent team
- `02_check_status.py` - Check execution status
- `03_get_results.py` - Retrieve execution results
- `04_list_executions.py` - List and filter executions

See [examples/README.md](examples/README.md) for detailed usage instructions.

**Quick start:**

```bash
# Run the complete workflow
python examples/00_full_workflow.py "Your research topic"

# Or step by step
python examples/01_spawn_agent_team.py
python examples/02_check_status.py <team_id>
python examples/03_get_results.py <team_id>
```

## Testing

The MCP server includes comprehensive test coverage:

- **Unit tests**: Fast tests with mocked dependencies
- **Integration tests**: Component interaction tests
- **E2E tests**: Full workflow tests with real backend
- **LibreChat simulation**: Simulated LibreChat interaction patterns

### Quick Start

```bash
# Run all tests (excludes E2E by default)
poetry run pytest

# Run with coverage
poetry run pytest --cov=mcp_server

# Run E2E tests (requires backend running)
./run_e2e_tests.sh

# Run LibreChat simulation tests
poetry run pytest tests/test_librechat_simulation.py -v
```

### Documentation

- [Testing Guide](TESTING_GUIDE.md) - Comprehensive testing documentation
- [E2E Testing](tests/README_E2E.md) - End-to-end integration tests
- [LibreChat Integration](LIBRECHAT_INTEGRATION.md) - LibreChat setup and testing

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=mcp_server

# Run specific test file
poetry run pytest tests/test_server_integration.py
```

### Project Structure

```
mcp_server/
├── __init__.py           # Package initialization
├── main.py               # Entry point and server startup
├── server.py             # MCP server implementation
├── fastapi_client.py     # FastAPI backend client
├── formatters.py         # JSON-LD response formatters
├── config.py             # Configuration management
├── errors.py             # Custom exception classes
├── pyproject.toml        # Project dependencies
└── tests/                # Test suite
    ├── test_server.py
    ├── test_fastapi_client.py
    └── test_formatters.py
```

## Troubleshooting

### Server won't start

- Ensure FastAPI backend is running at the configured URL
- Check that all dependencies are installed: `poetry install`
- Verify Python version is 3.10 or higher: `python --version`

### Tools not appearing in LibreChat

- Verify `mcp.json` configuration is correct
- Check LibreChat logs for MCP connection errors
- Ensure the command path is correct (use absolute paths if needed)
- Restart LibreChat after modifying `mcp.json`

### Execution not found errors

- Verify the execution ID is correct
- Check that the FastAPI backend database is accessible
- Ensure the execution was created successfully (check backend logs)

### Timeout errors

- Increase `HTTP_TIMEOUT` environment variable
- Check network connectivity to FastAPI backend
- Verify FastAPI backend is responding (test with curl/httpie)

## Contributing

See the main project's CONTRIBUTING.md for development guidelines.

## License

See the main project's LICENSE file.
