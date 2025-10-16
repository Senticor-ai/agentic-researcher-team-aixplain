# Logging Implementation Summary

This document summarizes the comprehensive logging implementation added to the MCP server codebase.

## Overview

Comprehensive logging has been added throughout the MCP server to provide visibility into:
- Tool invocations and their parameters
- Successful operations and their outcomes
- Error conditions with full stack traces
- Debug information for troubleshooting

## Log Levels

The logging system supports standard Python log levels, configurable via the `LOG_LEVEL` environment variable:

- **DEBUG**: Detailed information for diagnosing problems (tool arguments, response formatting details)
- **INFO**: Confirmation that things are working as expected (successful operations, status changes)
- **WARNING**: Indication of unexpected events or validation failures
- **ERROR**: Serious problems with full stack traces

## Configuration

### Environment Variable

Set the log level via environment variable:
```bash
export LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR, CRITICAL
```

### Log Output

All logs are written to **stderr** to avoid interfering with the stdio transport used for MCP communication. This ensures that:
- MCP protocol messages on stdout remain clean
- Logs can be captured separately by LibreChat or other clients
- Debugging doesn't break the communication channel

## Logging Coverage

### 1. Custom Exception Classes (`errors.py`)

Created custom exception classes with JSON-LD formatting:
- `MCPError`: Base exception with error code and message
- `ExecutionNotFoundError`: Raised when execution ID not found
- `ExecutionNotCompletedError`: Raised when results requested for incomplete execution
- `BackendUnavailableError`: Raised when FastAPI backend is unreachable

Each exception includes a `to_json_ld()` method for consistent error formatting.

### 2. Server Module (`server.py`)

#### Tool Invocation Logging
- **DEBUG**: Log tool name and arguments when invoked
- **DEBUG**: Log successful tool completion
- **WARNING**: Log unknown tool requests
- **ERROR**: Log tool execution errors with stack traces

#### spawn_agent_team Tool
- **WARNING**: Invalid parameters (empty topic, invalid interaction_limit)
- **INFO**: Team spawning initiated with parameters
- **INFO**: Successful team creation with team_id
- **ERROR**: HTTP errors and unexpected errors with stack traces

#### get_execution_status Tool
- **WARNING**: Invalid execution_id parameter
- **INFO**: Status check initiated
- **DEBUG**: Current status retrieved
- **DEBUG**: Entity count and duration calculations
- **INFO**: Successful status retrieval
- **WARNING**: Execution not found (404)
- **ERROR**: HTTP errors and unexpected errors with stack traces

#### get_execution_results Tool
- **WARNING**: Invalid execution_id parameter
- **INFO**: Results retrieval initiated
- **DEBUG**: Status check before retrieving results
- **WARNING**: Attempted retrieval for incomplete execution
- **DEBUG**: Sachstand retrieval
- **ERROR**: Missing sachstand content
- **INFO**: Successful results retrieval with entity count
- **WARNING**: Execution not found (404)
- **ERROR**: HTTP errors and unexpected errors with stack traces

#### list_executions Tool
- **WARNING**: Invalid filter parameters (limit, offset, status_filter)
- **INFO**: List request with filter parameters
- **INFO**: Successful retrieval with count
- **DEBUG**: List of execution IDs retrieved
- **ERROR**: HTTP errors and unexpected errors with stack traces

### 3. FastAPI Client (`fastapi_client.py`)

All HTTP operations include:
- **INFO**: Client initialization with base URL
- **DEBUG**: Request details (method, URL, payload)
- **INFO**: Successful responses with key data
- **ERROR**: Timeout and HTTP errors

### 4. Formatters (`formatters.py`)

Response formatting includes:
- **DEBUG**: Formatting operations with key identifiers
- **DEBUG**: Optional fields added (entity count, duration)
- **DEBUG**: Error response formatting

### 5. Configuration (`config.py`)

Configuration loading includes:
- Logger initialization (note: actual logging happens after setup_logging() in main.py)
- Configuration validation through Pydantic validators

### 6. Main Entry Point (`main.py`)

Already includes comprehensive logging:
- Server startup with configuration details
- Initialization success/failure
- Graceful shutdown on interrupt
- Fatal errors with stack traces

## Example Log Output

### DEBUG Level
```
2025-10-16 10:30:00 - mcp_server.server - DEBUG - Tool invoked: spawn_agent_team with arguments: {'topic': 'Kinderarmut', 'goals': [], 'interaction_limit': 50}
2025-10-16 10:30:00 - mcp_server.server - INFO - Spawning agent team for topic: 'Kinderarmut' with 0 goals and interaction_limit=50
2025-10-16 10:30:00 - mcp_server.fastapi_client - DEBUG - Creating team: POST http://localhost:8000/api/v1/agent-teams with payload={'topic': 'Kinderarmut', 'goals': [], 'interaction_limit': 50, 'mece_strategy': 'depth_first'}
2025-10-16 10:30:01 - mcp_server.fastapi_client - INFO - Team created successfully: team_id=abc-123
2025-10-16 10:30:01 - mcp_server.server - INFO - Agent team spawned successfully: team_id=abc-123
2025-10-16 10:30:01 - mcp_server.formatters - DEBUG - Formatting spawn response for team_id=abc-123, topic='Kinderarmut'
2025-10-16 10:30:01 - mcp_server.server - DEBUG - Tool spawn_agent_team completed successfully
```

### INFO Level
```
2025-10-16 10:30:00 - mcp_server.main - INFO - Starting librechat-osint-mcp v0.1.0
2025-10-16 10:30:00 - mcp_server.main - INFO - FastAPI Backend: http://localhost:8000
2025-10-16 10:30:00 - mcp_server.server - INFO - Spawning agent team for topic: 'Kinderarmut' with 0 goals and interaction_limit=50
2025-10-16 10:30:01 - mcp_server.server - INFO - Agent team spawned successfully: team_id=abc-123
```

### ERROR Level
```
2025-10-16 10:30:00 - mcp_server.server - ERROR - HTTP error while spawning team for topic 'Kinderarmut': Connection refused
Traceback (most recent call last):
  File "mcp_server/server.py", line 123, in spawn_agent_team
    response = await self.fastapi_client.create_team(...)
  ...
httpx.ConnectError: Connection refused
```

## Benefits

1. **Debugging**: DEBUG level provides detailed information for troubleshooting
2. **Monitoring**: INFO level shows operational status and successful operations
3. **Error Tracking**: ERROR level captures failures with full context
4. **Audit Trail**: All tool invocations are logged with parameters
5. **Performance Insights**: Duration and entity counts logged for completed executions
6. **Non-Intrusive**: Logs to stderr, doesn't interfere with MCP protocol

## Testing Logging

To test different log levels:

```bash
# Debug level (most verbose)
LOG_LEVEL=DEBUG python -m mcp_server.main

# Info level (default)
LOG_LEVEL=INFO python -m mcp_server.main

# Warning level (only warnings and errors)
LOG_LEVEL=WARNING python -m mcp_server.main

# Error level (only errors)
LOG_LEVEL=ERROR python -m mcp_server.main
```

## Future Enhancements

Potential improvements for logging:
1. Structured logging (JSON format) for log aggregation tools
2. Log rotation for long-running servers
3. Performance metrics logging (request duration, queue sizes)
4. Correlation IDs for tracking requests across components
5. Integration with external logging services (e.g., Sentry, DataDog)
