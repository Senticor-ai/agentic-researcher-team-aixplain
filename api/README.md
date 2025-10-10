# Honeycomb OSINT Management API

## Overview

This is the FastAPI-based Management API for the Honeycomb OSINT Agent Team System. It provides endpoints for creating and managing agent teams that conduct automated research.

## Implementation Status

✅ **Task 2: Implement minimal Management API** - COMPLETED

All subtasks completed:
- ✅ 2.1: FastAPI application with basic configuration
- ✅ 2.2: POST /api/v1/agent-teams endpoint
- ✅ 2.3: GET /api/v1/agent-teams endpoint
- ✅ 2.4: GET /api/v1/agent-teams/{team_id} endpoint

## API Endpoints

### Health Check
```
GET /api/v1/health
```
Returns API health status.

### Create Agent Team
```
POST /api/v1/agent-teams
Content-Type: application/json

{
  "topic": "Research topic",
  "goals": ["Goal 1", "Goal 2"],
  "interaction_limit": 50,
  "mece_strategy": "depth_first"
}
```
Creates a new agent team and returns team_id.

### List Agent Teams
```
GET /api/v1/agent-teams
```
Returns list of all agent teams with summary information.

### Get Agent Team Details
```
GET /api/v1/agent-teams/{team_id}
```
Returns detailed information about a specific agent team.

## Running the API

### Development Mode
```bash
python -m api.main
```

The API will start on `http://localhost:8000` (configurable via .env).

### Running Tests
```bash
python -m pytest tests/test_api.py -v
```

## Project Structure

```
api/
├── __init__.py       # Package initialization
├── main.py           # FastAPI application and endpoints
├── config.py         # Configuration management
├── models.py         # Pydantic data models
├── storage.py        # In-memory storage for agent teams
└── README.md         # This file
```

## Configuration

Configuration is loaded from environment variables (see `.env.example`):

- `AIXPLAIN_API_KEY`: Your aixplain API key (required)
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `ENVIRONMENT`: Environment name (default: development)

## Next Steps

The next task in the implementation plan is:
- **Task 3**: Integrate with aixplain Team Agents API
  - 3.1: Create aixplain client module
  - 3.2: Configure minimal agent team
  - 3.3: Implement agent spawning

## Testing

All endpoints have been tested and verified:
- ✅ Health check endpoint works
- ✅ Agent team creation works
- ✅ Agent team listing works
- ✅ Agent team detail retrieval works
- ✅ 404 handling for non-existent teams works

Run `python -m pytest tests/test_api.py -v` to verify.
