# Debugging & Logging Improvements

## Summary
Added comprehensive logging, raw execution trace storage, and server log capture to help debug agent execution failures. All server console logs are now captured per-team and visible in the web UI.

## Changes Made

### 1. Enhanced Backend Logging (`api/main.py`)
- Added detailed logging of the full agent response when received from aixplain
- Logs now include:
  - Output content
  - Completion status
  - Intermediate steps count
  - Data keys
  - Input/output/critiques from the agent
- Added error detection for "error occurred during execution" messages
- All logs are written to console when running the backend server

### 2. Raw Response Storage (`api/persistent_storage.py`)
- Added new database column: `raw_agent_response`
- Stores the completely unprocessed response from aixplain before any formatting
- New method: `set_raw_agent_response()` to store raw responses
- Updated `_team_to_dict()` to include raw response in team data

### 3. Raw Response API Endpoint (`api/main.py`)
- New endpoint: `GET /api/v1/agent-teams/{team_id}/raw-response`
- Returns complete debugging data:
  - `raw_agent_response`: Unprocessed response string from aixplain
  - `agent_response`: Processed/formatted response
  - `execution_log`: All execution steps
  - `sachstand`: Generated JSON-LD output
  - `mece_graph`: MECE decomposition if available
  - Team metadata (topic, status, timestamps)

### 4. Server Log Capture (`api/team_log_handler.py`)
- New custom logging handler: `TeamLogHandler`
- Captures all server logs (INFO, WARNING, ERROR) during team execution
- Uses context variables to associate logs with specific teams
- Stores logs with:
  - Timestamp
  - Log level
  - Logger name
  - Message
  - Module, function, and line number
- Automatically attached to Python's root logger

### 5. UI Server Logs Display (`ui/src/pages/TeamDetail.jsx`)
- New "Server Logs" section shows all captured server console logs
- Displays:
  - Timestamp
  - Log level (with color coding)
  - Logger name
  - Module/function/line information
  - Full log message
- Download button to export server logs as JSON
- Only shown when logs are available

### 6. UI Download Features (`ui/src/pages/TeamDetail.jsx`)
- Added "Debug & Analysis" section in team metadata
- **Download Complete Debug Data**: Downloads JSON file with:
  - Raw agent response (unprocessed)
  - Server logs (console output)
  - Execution log (team steps)
  - Agent response (processed)
  - Sachstand (JSON-LD output)
  - MECE graph
- File naming: `raw_execution_trace_{team_id}.json`

### 7. API Client Update (`ui/src/api/client.js`)
- Added `getRawResponse(id)` method to fetch raw execution data

## How to Use

### View Server Logs in Web UI
1. Navigate to a team detail page
2. Scroll down to the "Server Logs" section
3. See all server console logs captured during team execution
4. Logs include timestamps, levels, and source code locations
5. Click "Download" to export logs as JSON

### View Logs in Backend Terminal
When running the backend with `./start-backend.sh`, you'll now see detailed logs like:
```
Team {id}: ===== FULL AGENT RESPONSE =====
Team {id}: Output: {output_content}
Team {id}: Completed: True/False
Team {id}: Intermediate Steps Count: X
Team {id}: Data Keys: [...]
Team {id}: ===== END AGENT RESPONSE =====
```

All these logs are also captured and stored in the database for viewing in the UI.

### Download Complete Debug Data
1. Navigate to a team detail page
2. Scroll to the "Debug & Analysis" section
3. Click "Download Complete Debug Data"
4. Open the JSON file to see:
   - `raw_agent_response`: Exact response from aixplain (unprocessed)
   - `server_logs`: All server console logs
   - `execution_log`: Team execution steps
   - `agent_response`: Formatted agent response
   - `sachstand`: Generated JSON-LD output
   - `mece_graph`: MECE decomposition

## Debugging the Current Issue

For the failing team `fb0b7c9b-605c-43a3-8b63-d88841675847`:

1. **Download the raw trace** to see exactly what aixplain returned
2. **Check backend logs** for the detailed response logging
3. **Look for error messages** in the raw response that might explain why no entities were extracted

The agent response shows:
```json
{
  "output": "An error occurred during execution. Please contact your administrator for assistance."
}
```

This indicates an aixplain platform error, not a code issue. Possible causes:
- Tavily API key expired or invalid
- aixplain platform issues
- Tool configuration problems
- Rate limiting

## Next Steps

1. Restart the backend to apply logging changes
2. Create a new test team to see detailed logs
3. Download the raw trace from the failing team
4. Check if Tavily API key is still valid
5. Verify aixplain platform status
