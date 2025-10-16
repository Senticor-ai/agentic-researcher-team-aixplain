# Implementation Plan

- [x] 1. Set up MCP server project structure
  - Create `mcp_server/` directory with Python package structure
  - Create `__init__.py`, `main.py`, `server.py` files
  - Set up `pyproject.toml` with dependencies (mcp, httpx, aiosqlite, pydantic)
  - Create `.env.example` with configuration variables
  - _Requirements: 4.1, 4.2_

- [x] 2. Implement FastAPI client for backend communication
  - [x] 2.1 Create `mcp_server/fastapi_client.py` with FastAPIClient class
    - Implement `__init__` method with base_url configuration
    - Implement `create_team` method to POST /api/v1/agent-teams
    - Implement `get_team_status` method to GET /api/v1/agent-teams/{team_id}
    - Implement `get_sachstand` method to GET /api/v1/sachstand/{team_id}
    - Add error handling for HTTP errors and timeouts
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.2 Write unit tests for FastAPIClient
    - Mock HTTP requests using httpx mock
    - Test successful requests and response parsing
    - Test error handling (404, 500, timeout)
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 3. Enhance FastAPI client with list_teams method
  - [x] 3.1 Add `list_teams` method to FastAPIClient
    - Implement method to GET /api/v1/agent-teams
    - Support client-side filtering by topic and status (if backend doesn't support it)
    - Handle pagination if needed
    - Add error handling for HTTP errors
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 3.2 (Optional) Enhance FastAPI backend list endpoint
    - Add query parameters to GET /api/v1/agent-teams (topic, status, limit, offset)
    - Implement server-side filtering in the backend
    - This is optional - client-side filtering is acceptable for MVP
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Implement JSON-LD response formatters
  - [x] 4.1 Create `mcp_server/formatters.py` with response formatting functions
    - Implement `format_spawn_response` for spawn_agent_team tool
    - Implement `format_status_response` for get_execution_status tool
    - Implement `format_list_response` for list_executions tool
    - Implement `format_error_response` for error handling
    - Ensure all responses follow JSON-LD schema.org format
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.2 Write unit tests for formatters
    - Test each formatter with sample data
    - Validate JSON-LD structure and required fields
    - Test error response formatting
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Implement MCP server with tool handlers
  - [x] 5.1 Create `mcp_server/server.py` with LibreChatMCPServer class
    - Implement `__init__` method with FastAPIClient initialization
    - Set up MCP server instance with tool definitions (spawn_agent_team, get_execution_status, get_execution_results, list_executions)
    - Keep server completely stateless - all state managed by FastAPI backend
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 5.2 Implement spawn_agent_team tool handler
    - Validate input parameters (topic, goals, interaction_limit)
    - Call FastAPIClient.create_team to spawn agent team
    - Format response with execution ID and status
    - Handle errors and return formatted error responses
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 5.3 Implement get_execution_status tool handler
    - Validate execution_id parameter
    - Call FastAPIClient.get_team_status to get execution details
    - Format status response with entity count if completed
    - Handle execution not found error (404 from backend)
    - _Requirements: 2.1, 2.2, 2.5_

  - [x] 5.4 Implement get_execution_results tool handler
    - Validate execution_id parameter
    - Call FastAPIClient.get_sachstand to get JSON-LD results
    - Return full JSON-LD sachstand if completed
    - Handle 404 error if execution not found or not completed
    - Return helpful error message with current status if not ready
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4_

  - [x] 5.5 Implement list_executions tool handler
    - Validate filter parameters (topic_filter, status_filter, limit)
    - Call FastAPIClient.list_teams to get all teams
    - Apply client-side filtering by topic and status if needed
    - Format response as JSON-LD ItemList
    - Handle empty results gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 5.6 Write integration tests for MCP server
    - Test each tool handler with mocked dependencies
    - Test error handling for each tool
    - Test parameter validation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 6. Implement main entry point and configuration
  - [x] 6.1 Create `mcp_server/main.py` with server startup
    - Load configuration from environment variables (FASTAPI_BASE_URL)
    - Initialize FastAPIClient with base URL
    - Create and run stateless MCP server instance
    - Add logging configuration
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 6.2 Create configuration module `mcp_server/config.py`
    - Define configuration class with environment variable loading
    - Add validation for required configuration
    - Set default values for optional configuration
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 7. Add error handling and logging
  - [x] 7.1 Create `mcp_server/errors.py` with custom exception classes
    - Define MCPError base class
    - Define ExecutionNotFoundError
    - Define ExecutionNotCompletedError
    - Define BackendUnavailableError
    - _Requirements: 1.4, 2.4, 3.5_

  - [x] 7.2 Add comprehensive logging throughout the codebase
    - Add debug logging for all tool invocations
    - Add info logging for successful operations
    - Add error logging with stack traces for failures
    - Configure log levels via environment variable
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 8. Create documentation and examples
  - [x] 8.1 Create README.md for MCP server
    - Document installation instructions
    - Document configuration options
    - Provide usage examples for each tool
    - Include LibreChat mcp.json configuration example
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 8.2 Create example scripts for testing
    - Create example script to spawn agent team
    - Create example script to check status
    - Create example script to retrieve results
    - Create example script to list executions
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 9. End-to-end integration testing
  - [x] 9.1 Create integration test script
    - Test full workflow: spawn → check status → retrieve results
    - Test with actual FastAPI backend running
    - Verify JSON-LD response format
    - Test error handling (backend down, invalid IDs, etc.)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 9.2 Test LibreChat integration
    - Configure MCP server in LibreChat mcp.json
    - Test tool discovery in LibreChat
    - Test spawning agent team from LibreChat chat
    - Test checking status from LibreChat
    - Test retrieving results from LibreChat
    - Verify JSON-LD rendering in LibreChat UI
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
