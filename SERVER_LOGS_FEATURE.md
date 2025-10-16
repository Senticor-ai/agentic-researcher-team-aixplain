# Server Logs in Web UI - Feature Summary

## What Was Implemented

We've added a complete server log capture system that makes all backend console logs visible in the web UI.

## Key Features

### 1. Automatic Log Capture
- All Python logging output (INFO, WARNING, ERROR) is automatically captured
- Logs are associated with specific teams using context variables
- No manual logging needed - works with existing `logger.info()`, `logger.error()`, etc.

### 2. Rich Log Data
Each log entry includes:
- **Timestamp**: When the log was created
- **Level**: INFO, WARNING, ERROR, etc.
- **Logger**: Which Python logger created it (e.g., `__main__`, `api.entity_processor`)
- **Message**: The actual log message
- **Source**: Module name, function name, and line number

### 3. Web UI Display
- New "Server Logs" section on team detail pages
- Color-coded by log level (blue for INFO, orange for WARNING, red for ERROR)
- Shows source code location for debugging
- Download button to export logs as JSON

### 4. Complete Debug Package
The "Download Complete Debug Data" button now includes:
- Raw agent response (unprocessed from aixplain)
- **Server logs** (all console output)
- Execution log (team steps)
- Agent response (processed)
- Sachstand (JSON-LD output)
- MECE graph

## Technical Implementation

### Backend (`api/team_log_handler.py`)
```python
# Custom logging handler that captures logs per team
class TeamLogHandler(logging.Handler):
    def emit(self, record):
        # Get current team_id from context
        # Format log entry with all metadata
        # Store in database
```

### Context Management
```python
# Set team context at start of execution
set_team_context(team_id)

# All logs within this context are captured
logger.info("This will be captured")

# Clear context when done
clear_team_context()
```

### Database Storage
- New column: `server_logs` (JSON array)
- Each log entry is a structured object
- Appended in real-time during execution

## Benefits

1. **No More Terminal Hunting**: All logs are in the UI, no need to scroll through terminal output
2. **Persistent**: Logs are saved in the database, available even after server restart
3. **Per-Team**: Each team has its own isolated log history
4. **Downloadable**: Export logs for offline analysis or sharing
5. **Structured**: Logs include metadata for better debugging

## Example Use Case

When debugging the failing team `fb0b7c9b-605c-43a3-8b63-d88841675847`:

1. Open the team detail page
2. Scroll to "Server Logs" section
3. See exactly what the server logged:
   ```
   [INFO] Team fb0b7c9b...: Creating team agent for topic: Familienforum Markdorf
   [INFO] Team fb0b7c9b...: ===== FULL AGENT RESPONSE =====
   [ERROR] Team fb0b7c9b...: Agent execution failed: An error occurred...
   ```
4. Download the complete debug data for deeper analysis

## What's Next

To see this in action:
1. Restart the backend to apply changes
2. Create a new test team
3. View the "Server Logs" section on the team detail page
4. See all backend logs captured in real-time
