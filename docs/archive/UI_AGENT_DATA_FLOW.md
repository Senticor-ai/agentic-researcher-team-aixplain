# UI Agent Data Flow Documentation

## How the UI Gets Agent Details

The UI displays agent information from **two sources**:

### 1. Static Configuration (Pre-configured Setup)
### 2. Dynamic Execution Data (Actual Agent Activity)

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    UI COMPONENTS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TeamConfigInfo.jsx                TeamDetail.jsx           │
│  (Static Config)                   (Dynamic Execution)      │
│         │                                  │                │
│         │                                  │                │
│         ▼                                  ▼                │
│  Hardcoded Agent List          API: /agent-teams/{id}       │
│  - Built-in agents             API: /agent-teams/{id}/trace │
│  - User-defined agents         API: /execution-stats        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  main.py                                                    │
│  ├─ get_agent_configuration()                              │
│  │  └─ Reads from team_config.py                           │
│  │     └─ Checks TeamConfig.TOOL_IDS                        │
│  │                                                          │
│  ├─ /execution-stats                                        │
│  │  └─ Returns agent_configuration                          │
│  │                                                          │
│  └─ /agent-teams/{id}/trace                                │
│     └─ Returns intermediate_steps with agent names          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 TEAM CONFIGURATION                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  team_config.py                                             │
│  └─ TeamConfig.TOOL_IDS                                     │
│     ├─ "tavily_search": "6736411cf127849667606689"          │
│     └─ "wikipedia": "6633fd59821ee31dd914e232"              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Static Configuration Display

### Component: `TeamConfigInfo.jsx`

**Purpose**: Shows the pre-configured team setup (what agents are available)

**Data Source**: Hardcoded in the component

```javascript
const teamConfig = {
  builtInAgents: [
    { name: "Mentalist", role: "Strategic Planner", ... },
    { name: "Inspector", role: "Quality Monitor", ... },
    // ... other built-in agents
  ],
  userDefinedAgents: [
    { name: "Search Agent", tools: ["Tavily Search API"], ... },
    { name: "Wikipedia Agent", tools: ["Wikipedia API"], ... }
  ]
};
```

**Why Hardcoded?**
- Shows the **available** agents, not necessarily the ones used
- Provides consistent UI even before any teams are created
- Serves as documentation of the system capabilities

**Location in UI**: 
- Dashboard page
- "Agent Team Configuration" card
- Expandable details section

---

## 2. Dynamic Execution Data

### Component: `TeamDetail.jsx`

**Purpose**: Shows actual agent activity during execution

**Data Sources**: Multiple API endpoints

#### A. Agent Execution Trace

**API Endpoint**: `GET /api/v1/agent-teams/{team_id}/trace`

**Returns**:
```json
{
  "team_id": "uuid",
  "trace": [
    {
      "step_number": 1,
      "agent_name": "Search Agent",
      "agent_type": "search",
      "input": "...",
      "output": "...",
      "tool_steps": [...]
    },
    {
      "step_number": 2,
      "agent_name": "Wikipedia Agent",
      "agent_type": "wikipedia",
      "input": "...",
      "output": "..."
    }
  ]
}
```

**How It Works**:
1. Backend extracts `intermediate_steps` from aixplain agent response
2. Parses each step to identify agent name and type
3. UI displays each step with color-coded badges
4. Agent type determines the color (via `getAgentTypeColor()`)

**Agent Type Detection**:
```python
# In api/main.py
def parse_agent_type(agent_name: str) -> str:
    name_lower = agent_name.lower()
    if 'mentalist' in name_lower:
        return 'mentalist'
    elif 'search' in name_lower:
        return 'search'
    elif 'wikipedia' in name_lower:
        return 'wikipedia'
    # ... etc
```

#### B. Execution Statistics

**API Endpoint**: `GET /api/v1/agent-teams/{team_id}/execution-stats`

**Returns**:
```json
{
  "agent_configuration": {
    "built_in_agents": [...],
    "user_defined_agents": [
      {
        "name": "Search Agent",
        "tools": ["Tavily Search"],
        "description": "..."
      },
      {
        "name": "Wikipedia Agent",
        "tools": ["Wikipedia"],
        "description": "..."
      }
    ]
  },
  "execution_data": {
    "runtime": 12.5,
    "credits": 0.05,
    "assets_used": ["Search Agent", "Wikipedia Agent"]
  }
}
```

**How It Works**:
1. Backend calls `get_agent_configuration()` function
2. Function checks `TeamConfig.TOOL_IDS` to see what's configured
3. Dynamically builds agent list based on configuration
4. Returns to UI for display

**Dynamic Configuration Logic**:
```python
def get_agent_configuration():
    # Always include Search Agent
    user_defined_agents = [
        {"name": "Search Agent", "tools": ["Tavily Search"], ...}
    ]
    
    # Add Wikipedia Agent if configured
    if TeamConfig.TOOL_IDS.get("wikipedia"):
        user_defined_agents.append({
            "name": "Wikipedia Agent",
            "tools": ["Wikipedia"],
            ...
        })
    
    return {
        "built_in_agents": [...],
        "user_defined_agents": user_defined_agents
    }
```

---

## 3. Agent Color Coding

### UI Component: `TeamDetail.jsx`

**Function**: `getAgentTypeColor(agentType)`

```javascript
const getAgentTypeColor = (agentType) => {
  const colors = {
    'mentalist': '#9b59b6',      // Purple
    'orchestrator': '#3498db',   // Blue
    'inspector': '#e74c3c',      // Red
    'search': '#2ecc71',         // Green
    'wikipedia': '#e67e22',      // Orange
    'response': '#f39c12',       // Yellow
    'unknown': '#95a5a6'         // Gray
  };
  return colors[agentType?.toLowerCase()] || colors.unknown;
};
```

**Usage**:
- Applied to agent badges in execution trace
- Border colors for step cards
- Consistent across the UI

---

## 4. Data Synchronization

### When Wikipedia Agent is Added

**Backend Changes**:
1. ✅ `team_config.py` - Wikipedia tool ID configured
2. ✅ `main.py` - `get_agent_configuration()` checks for Wikipedia tool
3. ✅ API returns Wikipedia agent in `/execution-stats`

**Frontend Changes**:
1. ✅ `TeamConfigInfo.jsx` - Wikipedia agent added to static config
2. ✅ `TeamDetail.jsx` - Wikipedia color added to `getAgentTypeColor()`
3. ✅ UI displays Wikipedia agent in both static and dynamic views

### Data Flow for New Team Creation

```
1. User creates team
   └─> POST /api/v1/agent-teams
       └─> Backend calls TeamConfig.create_team()
           └─> Checks if Wikipedia tool configured
               └─> Creates team with/without Wikipedia agent

2. Team executes
   └─> aixplain runs agents
       └─> Mentalist may invoke Wikipedia Agent
           └─> intermediate_steps includes Wikipedia Agent activity

3. UI polls for updates
   └─> GET /agent-teams/{id}/trace
       └─> Receives Wikipedia Agent steps
           └─> Displays with orange color badge

4. UI shows stats
   └─> GET /execution-stats
       └─> Returns agent_configuration with Wikipedia Agent
           └─> Shows in "Assets Used" section
```

---

## 5. Current Implementation Status

### ✅ Fully Implemented

1. **Backend Configuration**:
   - Wikipedia tool ID configured in `team_config.py`
   - Dynamic agent configuration in `main.py`
   - Wikipedia agent created when tool is available

2. **API Endpoints**:
   - `/execution-stats` returns Wikipedia agent dynamically
   - `/trace` includes Wikipedia agent steps
   - Agent type detection recognizes "wikipedia"

3. **UI Display**:
   - Static config shows Wikipedia agent
   - Execution trace displays Wikipedia steps
   - Color coding applied (orange #e67e22)

### 🔄 How It Works Together

**Static Display (TeamConfigInfo)**:
- Shows what agents **can** be used
- Hardcoded for consistency
- Updated manually when new agents added

**Dynamic Display (TeamDetail)**:
- Shows what agents **were actually** used
- Reads from API responses
- Automatically updates based on execution

**Configuration Source (team_config.py)**:
- Single source of truth for tool IDs
- Backend reads this to determine available agents
- API returns configuration based on this

---

## 6. Future Improvements

### Option 1: Fully Dynamic Configuration

Make the static config also read from API:

```javascript
// TeamConfigInfo.jsx
const [agentConfig, setAgentConfig] = useState(null);

useEffect(() => {
  // Fetch agent configuration from API
  fetch('/api/v1/agent-configuration')
    .then(res => res.json())
    .then(data => setAgentConfig(data));
}, []);
```

**Pros**:
- Single source of truth
- No manual UI updates needed
- Always in sync with backend

**Cons**:
- Requires API call on page load
- More complex state management

### Option 2: Configuration Endpoint

Create dedicated endpoint for agent configuration:

```python
@app.get("/api/v1/agent-configuration")
async def get_agent_configuration_endpoint():
    """Get current agent configuration"""
    return get_agent_configuration()
```

**Benefits**:
- UI can fetch configuration on demand
- Reusable across components
- Easy to extend

---

## Summary

**How UI Gets Agent Details**:

1. **Static Config** (TeamConfigInfo.jsx):
   - Hardcoded agent list
   - Shows available agents
   - Updated manually

2. **Dynamic Execution** (TeamDetail.jsx):
   - Fetches from `/trace` endpoint
   - Shows actual agent activity
   - Updates automatically

3. **Configuration API** (main.py):
   - Reads from `team_config.py`
   - Returns agent configuration
   - Dynamically includes Wikipedia agent if configured

**Key Files**:
- `api/team_config.py` - Tool configuration (source of truth)
- `api/main.py` - API endpoints and agent configuration logic
- `ui/src/components/TeamConfigInfo.jsx` - Static agent display
- `ui/src/pages/TeamDetail.jsx` - Dynamic execution display

**Wikipedia Agent Integration**:
- ✅ Backend: Configured and dynamic
- ✅ API: Returns Wikipedia agent when configured
- ✅ UI: Displays in both static and dynamic views
- ✅ Colors: Orange (#e67e22) consistently applied
