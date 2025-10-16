# MCP Server Examples

This directory contains example scripts demonstrating how to interact with the OSINT agent team system through the FastAPI backend.

## Prerequisites

1. FastAPI backend must be running:
   ```bash
   # From the project root
   ./start-backend.sh
   ```

2. Install dependencies:
   ```bash
   cd mcp_server
   poetry install
   ```

## Example Scripts

### 1. Spawn Agent Team

Spawn a new agent team to research a topic.

```bash
python examples/01_spawn_agent_team.py
```

This will:
- Create a new agent team for the topic "Kinderarmut in Deutschland"
- Return a team ID for tracking the execution
- Display next steps for checking status and retrieving results

**Output:**
```
Spawning agent team for topic: 'Kinderarmut in Deutschland'
Goals: ['Identify key statistics and trends', ...]
Interaction limit: 50
------------------------------------------------------------
✓ Agent team spawned successfully!
  Team ID: abc123-def456-...
  Status: pending
  Created: 2025-10-16T10:30:00Z

Next steps:
  1. Check status: python examples/02_check_status.py abc123-def456-...
  2. Get results: python examples/03_get_results.py abc123-def456-...
```

### 2. Check Execution Status

Check the status of a running or completed execution.

```bash
python examples/02_check_status.py <team_id>
```

**Example:**
```bash
python examples/02_check_status.py abc123-def456-...
```

**Output (running):**
```
Checking status for execution: abc123-def456-...
------------------------------------------------------------
Topic: Kinderarmut in Deutschland
Status: running
Created: 2025-10-16T10:30:00Z
Updated: 2025-10-16T10:31:00Z

⏳ Execution is still running...
   Check again in a few moments.
```

**Output (completed):**
```
Checking status for execution: abc123-def456-...
------------------------------------------------------------
Topic: Kinderarmut in Deutschland
Status: completed
Created: 2025-10-16T10:30:00Z
Updated: 2025-10-16T10:35:00Z
Entities found: 15

✓ Execution completed successfully!
  Get results: python examples/03_get_results.py abc123-def456-...
```

### 3. Get Execution Results

Retrieve the full JSON-LD results from a completed execution.

```bash
python examples/03_get_results.py <team_id>
```

**Example:**
```bash
python examples/03_get_results.py abc123-def456-...
```

**Output:**
```
Retrieving results for execution: abc123-def456-...
------------------------------------------------------------
Topic: Kinderarmut in Deutschland
Entities found: 15

Entity breakdown:
  Organization: 5
  Person: 7
  Policy: 3

Sample entities:
  1. [Person] Dr. Jane Smith
     Climate policy expert and researcher...

  2. [Organization] Bundesministerium für Familie
     Federal ministry responsible for family affairs...

  3. [Policy] Kindergrundsicherung
     New policy initiative to combat child poverty...

  ... and 12 more entities

✓ Full results saved to: results_abc123-def456-....json
```

The full JSON-LD results are saved to a file for further analysis.

### 4. List Executions

List and filter historical executions.

```bash
python examples/04_list_executions.py [options]
```

**Options:**
- `--topic <filter>`: Filter by topic substring (case-insensitive)
- `--status <status>`: Filter by status (pending, running, completed, failed)
- `--limit <n>`: Maximum number of results (default: 10)

**Examples:**

List all executions:
```bash
python examples/04_list_executions.py
```

List only completed executions:
```bash
python examples/04_list_executions.py --status completed
```

Filter by topic:
```bash
python examples/04_list_executions.py --topic climate
```

Combine filters:
```bash
python examples/04_list_executions.py --topic policy --status completed --limit 5
```

**Output:**
```
Listing executions
  Status filter: completed
  Limit: 10
------------------------------------------------------------
Found 3 execution(s):

1. ✓ Kinderarmut in Deutschland
   ID: abc123-def456-...
   Status: completed
   Created: 2025-10-16T10:30:00Z
   Entities: 15

2. ✓ Climate policy in Germany
   ID: def456-ghi789-...
   Status: completed
   Created: 2025-10-16T09:15:00Z
   Entities: 22

3. ✓ Digital transformation initiatives
   ID: ghi789-jkl012-...
   Status: completed
   Created: 2025-10-16T08:00:00Z
   Entities: 18

Commands:
  Check status: python examples/02_check_status.py <team_id>
  Get results:  python examples/03_get_results.py <team_id>
```

## Complete Workflow Example

Here's a complete workflow from spawning a team to retrieving results:

```bash
# 1. Spawn an agent team
python examples/01_spawn_agent_team.py
# Output: Team ID: abc123-def456-...

# 2. Wait a moment, then check status
python examples/02_check_status.py abc123-def456-...
# Output: Status: running

# 3. Wait for completion (typically 1-2 minutes)
# Check status again
python examples/02_check_status.py abc123-def456-...
# Output: Status: completed, Entities found: 15

# 4. Retrieve the full results
python examples/03_get_results.py abc123-def456-...
# Output: Full results saved to: results_abc123-def456-....json

# 5. List all completed executions
python examples/04_list_executions.py --status completed
```

## Customizing Examples

You can modify the example scripts to test different scenarios:

### Custom Topic and Goals

Edit `01_spawn_agent_team.py`:

```python
topic = "Your custom topic here"
goals = [
    "Your first research goal",
    "Your second research goal"
]
interaction_limit = 50  # Adjust as needed
```

### Different Backend URL

If your FastAPI backend is running on a different host or port:

```python
client = FastAPIClient(base_url="http://your-host:your-port")
```

### Polling for Completion

Create a script that polls until completion:

```python
import asyncio
from mcp_server.fastapi_client import FastAPIClient

async def wait_for_completion(team_id, poll_interval=10):
    client = FastAPIClient(base_url="http://localhost:8000")
    
    while True:
        response = await client.get_team_status(team_id)
        status = response.get("status")
        
        if status == "completed":
            print("✓ Execution completed!")
            return response
        elif status == "failed":
            print("✗ Execution failed!")
            return response
        
        print(f"Status: {status}, waiting {poll_interval}s...")
        await asyncio.sleep(poll_interval)
```

## Troubleshooting

### Connection Refused

If you get a connection error:
```
Error: Connection refused
```

Make sure the FastAPI backend is running:
```bash
# From project root
./start-backend.sh
```

### Team Not Found

If you get a "team not found" error:
```
Error: Execution with ID xyz not found
```

- Verify the team ID is correct
- Check that the team was created successfully
- Ensure the database is accessible

### Import Errors

If you get import errors:
```
ModuleNotFoundError: No module named 'mcp_server'
```

Make sure you're running from the correct directory and dependencies are installed:
```bash
cd mcp_server
poetry install
python examples/01_spawn_agent_team.py
```

## Next Steps

After testing with these examples, you can:

1. **Integrate with LibreChat**: Configure the MCP server in LibreChat's `mcp.json`
2. **Build custom tools**: Use these examples as a foundation for your own integrations
3. **Automate workflows**: Create scripts that combine multiple operations
4. **Analyze results**: Process the JSON-LD output for further analysis

See the main [README.md](../README.md) for more information about LibreChat integration.
