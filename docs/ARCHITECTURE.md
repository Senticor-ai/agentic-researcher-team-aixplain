# Honeycomb OSINT Agent Team System - Architecture

## Overview

The Honeycomb OSINT Agent Team System is designed to enable automated web research using aixplain's team agent framework. The system follows a **dynamic coordination** approach where agents plan and coordinate adaptively rather than following predefined workflows.

## Core Principles

### 1. API Invokes, Monitors, Stores - Agents Do the Work

The API layer is responsible for:
- **Invoking** agent teams via aixplain SDK
- **Monitoring** execution progress and logging
- **Storing** results and metadata in SQLite

The API does NOT:
- Extract entities (agents do this)
- Perform web searches (agents use tools)
- Make research decisions (Mentalist plans dynamically)

### 2. Dynamic Planning, Not Workflows

**We do NOT use predefined workflows.** Instead:
- The **Mentalist** creates dynamic research strategies based on the topic
- The **Orchestrator** spawns agents as needed (not in a fixed sequence)
- Agents can be invoked multiple times or in different orders
- No `WorkflowTask` is used - everything is adaptive

This allows the system to:
- Adapt to different research topics
- Handle complex, multi-faceted queries
- Recover from failures gracefully
- Scale research depth based on available information

### 3. JSON-LD as Output Format

All research results are formatted as JSON-LD using schema.org vocabulary:
- **ResearchReport** as the root type
- **Person** and **Organization** entities with properties
- **WebPage** citations with URLs and excerpts
- Completion status tracking (complete/partial/failed)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend UI                          │
│  (React + Blueprint.js - Monitoring & Visualization)        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                         │
│  • REST API endpoints                                        │
│  • Background task execution                                 │
│  • SQLite persistent storage                                 │
│  • Entity processing & JSON-LD generation                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ aixplain SDK
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   aixplain Team Agent                        │
│                                                              │
│  Built-in Micro Agents (Automatic):                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Mentalist: Dynamic strategy planning             │    │
│  │ • Inspector: Quality review (steps + output)       │    │
│  │ • Orchestrator: Agent spawning & coordination      │    │
│  │ • Feedback Combiner: Consolidates reviews          │    │
│  │ • Response Generator: Final output synthesis       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  User-Defined Agents:                                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Search Agent: Tavily Search tool                 │    │
│  │   - Web search & information gathering             │    │
│  │   - Entity extraction (Person, Organization)       │    │
│  │   - Source citation with URLs & excerpts           │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Agent Team Configuration

### Built-in Micro Agents

These agents are automatically included by aixplain's `TeamAgentFactory`:

1. **Mentalist** (Strategic Planner)
   - Analyzes research topic and goals
   - Creates dynamic research strategy
   - Plans on-the-fly, NOT following fixed workflows
   - Coordinates other agents based on needs

2. **Inspector** (Quality Monitor)
   - Reviews intermediate steps for quality
   - Reviews final output for completeness
   - Provides feedback throughout execution
   - Targets: `["steps", "output"]`

3. **Orchestrator** (Agent Spawner)
   - Routes tasks to appropriate agents
   - Spawns agents as needed (not predetermined)
   - Handles agent coordination dynamically

4. **Feedback Combiner** (Feedback Aggregator)
   - Consolidates inspection feedback
   - Aggregates reviews from multiple points

5. **Response Generator** (Output Synthesizer)
   - Creates final structured output
   - Synthesizes results from all agents
   - Formats output for API consumption

### User-Defined Agents

1. **Search Agent**
   - **Tool:** Tavily Search API
   - **Capabilities:**
     - Web search and information gathering
     - Entity extraction (Person, Organization)
     - Source citation with URLs and excerpts
     - Authoritative source prioritization
   - **Invocation:** Called by Orchestrator when Mentalist plans research tasks
   - **Output:** JSON with entities array and source citations

## Data Flow

### 1. Team Creation

```
User Request → API → TeamConfig.create_team()
                  ↓
            aixplain TeamAgentFactory
                  ↓
            Team Agent Created
                  ↓
            Background Task Started
```

### 2. Research Execution (Dynamic)

```
Mentalist: Analyzes topic → Creates dynamic plan
     ↓
Orchestrator: Routes to Search Agent (as needed)
     ↓
Search Agent: Uses Tavily → Extracts entities
     ↓
Inspector: Reviews results → Provides feedback
     ↓
Feedback Combiner: Consolidates reviews
     ↓
Response Generator: Creates final output
     ↓
API: Receives response → Formats to JSON-LD → Stores
```

**Note:** This is NOT a fixed sequence. The Mentalist may:
- Call Search Agent multiple times
- Request different types of searches
- Adjust strategy based on results
- Skip or repeat steps as needed

### 3. Data Storage

```
Agent Response → EntityProcessor.process_agent_response()
                      ↓
                 Validate entities
                      ↓
                 Generate JSON-LD
                      ↓
                 Store in SQLite
                      ↓
                 Write to file (output/)
```

## Technology Stack

### Backend
- **Framework:** FastAPI
- **Storage:** SQLite (via custom repository)
- **Agent SDK:** aixplain Python SDK
- **Models:** Pydantic for validation
- **Background Tasks:** FastAPI BackgroundTasks

### Frontend
- **Framework:** React 18
- **UI Library:** Blueprint.js (bright mode)
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Build Tool:** Vite

### External Services
- **aixplain:** Team agent orchestration and LLM access
- **Tavily Search:** Web search and information retrieval

## Storage Schema

### SQLite Tables

**teams** table:
```sql
CREATE TABLE teams (
    team_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    goals TEXT,  -- JSON array
    status TEXT NOT NULL,
    interaction_limit INTEGER,
    mece_strategy TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    execution_log TEXT,  -- JSON array
    agent_response TEXT,  -- JSON object
    sachstand TEXT,  -- JSON-LD object
    aixplain_agent_id TEXT
)
```

## API Endpoints

### Core Endpoints

- `POST /api/v1/agent-teams` - Create new team
- `GET /api/v1/agent-teams` - List all teams (sorted newest first)
- `GET /api/v1/agent-teams/{team_id}` - Get team details
- `GET /api/v1/agent-teams/{team_id}/trace` - Get execution trace
- `GET /api/v1/agent-teams/{team_id}/execution-stats` - Get execution statistics
- `GET /api/v1/sachstand/{team_id}` - Get JSON-LD Sachstand
- `GET /api/v1/health` - Health check

### Response Models

All responses use Pydantic models for validation:
- `AgentTeamResponse` - Team creation response
- `AgentTeamSummary` - List view with entity count
- `AgentTeamDetail` - Full team details with logs and output
- `PersonEntity` / `OrganizationEntity` - Entity models

## Configuration

### Environment Variables

```bash
# Required
AIXPLAIN_API_KEY=your_key_here

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DB_PATH=./data/teams.db
```

### Team Configuration

Located in `api/team_config.py`:

```python
MODELS = {
    "testing": "669a63646eb56306647e1091",  # GPT-4o Mini
    "production": "6646261c6eb563165658bbb1"  # GPT-4o
}

TOOL_IDS = {
    "tavily_search": "6736411cf127849667606689"
}
```

### Default Settings

- **Interaction Limit:** 50 steps
- **MECE Strategy:** depth_first
- **Inspector Targets:** ["steps", "output"]
- **Number of Inspectors:** 1
- **Model:** GPT-4o Mini (testing mode)

## Error Handling

### API Level
- HTTP status codes (404, 500, etc.)
- Structured error responses
- CORS configuration for UI

### Agent Level
- Execution logs capture all errors
- Status tracking (pending → running → completed/failed)
- Troubleshooting tips in UI for common issues

### Storage Level
- Automatic database creation
- Transaction safety
- Graceful degradation

## Security Considerations

1. **API Keys:** Stored in environment variables, never committed
2. **CORS:** Restricted to known frontend ports
3. **Input Validation:** Pydantic models validate all inputs
4. **SQL Injection:** Parameterized queries via sqlite3
5. **Rate Limiting:** Controlled by aixplain interaction limits

## Performance Considerations

1. **Background Tasks:** Long-running agent execution doesn't block API
2. **Auto-refresh:** UI polls every 3 seconds for running teams
3. **Pagination:** Not yet implemented (future enhancement)
4. **Caching:** Not yet implemented (future enhancement)
5. **Database Indexing:** Primary key on team_id

## Future Enhancements

1. **Wikipedia Tool:** Enrich entities with Wikipedia data
2. **Multiple Search Strategies:** Different approaches for different topics
3. **Entity Relationships:** Track connections between entities
4. **Advanced Filtering:** Search and filter in UI
5. **Export Formats:** CSV, PDF, etc.
6. **User Authentication:** Multi-user support
7. **Webhooks:** Notify external systems on completion
