# Contributing to Honeycomb OSINT Agent Team System

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (Python package manager)
- aixplain API key

### Initial Setup

1. **Clone and install backend:**
```bash
poetry install
poetry shell
cp .env.example .env
# Edit .env and add your AIXPLAIN_API_KEY
```

2. **Install frontend:**
```bash
cd ui
npm install
```

3. **Start development servers:**
```bash
# Terminal 1: Backend
python -m api.main

# Terminal 2: Frontend
cd ui && npm run dev
```

## Project Structure

```
.
├── api/                          # FastAPI backend
│   ├── main.py                  # API entry point & endpoints
│   ├── models.py                # Pydantic data models
│   ├── persistent_storage.py   # SQLite repository
│   ├── team_config.py           # Agent team configuration
│   └── entity_processor.py      # JSON-LD generation
├── ui/                          # React frontend
│   ├── src/
│   │   ├── api/client.js       # API client
│   │   ├── pages/              # Dashboard, TeamDetail
│   │   ├── components/         # Reusable components
│   │   └── App.jsx             # Main app component
│   └── package.json
├── data/                        # SQLite database (auto-created)
├── output/                      # Generated JSON-LD files
├── tests/                       # Test files
├── .kiro/specs/                 # Feature specs and tasks
└── docs/                        # Documentation
```

## Development Workflow

### 1. Working on Backend Features

**File locations:**
- API endpoints: `api/main.py`
- Data models: `api/models.py`
- Storage: `api/persistent_storage.py`
- Agent config: `api/team_config.py`
- Entity processing: `api/entity_processor.py`

**After making changes:**
```bash
# Restart the backend server (Ctrl+C and restart)
python -m api.main

# Run tests
./scripts/run_e2e_tests.sh
```

**Common tasks:**
- Adding new endpoints: Edit `api/main.py`
- Changing data models: Edit `api/models.py` (restart required)
- Modifying agent behavior: Edit `api/team_config.py`
- Adjusting entity extraction: Edit `api/entity_processor.py`

### 2. Working on Frontend Features

**File locations:**
- Pages: `ui/src/pages/`
- Components: `ui/src/components/`
- API client: `ui/src/api/client.js`
- Styles: Component-specific `.css` files

**After making changes:**
```bash
# Hot reload is automatic with Vite
# Just save the file and check the browser

# Build for production
npm run build

# Run E2E tests
npm run test:e2e
```

**Common tasks:**
- Adding new pages: Create in `ui/src/pages/` and add route in `App.jsx`
- Creating components: Add to `ui/src/components/`
- Styling: Use Blueprint.js components + custom CSS
- API calls: Use `agentTeamsAPI` from `ui/src/api/client.js`

### 3. Working with Agent Configuration

**Location:** `api/team_config.py`

**Key concepts:**
- **NO WorkflowTask:** We use dynamic planning, not predefined workflows
- **Mentalist plans:** The Mentalist creates strategies on-the-fly
- **Orchestrator coordinates:** Spawns agents as needed
- **Search Agent:** User-defined agent with Tavily tool

**Example: Adding a new tool**
```python
# 1. Add tool ID
TOOL_IDS = {
    "tavily_search": "6736411cf127849667606689",
    "new_tool": "your_tool_id_here"
}

# 2. Get tool in get_tools()
new_tool = ToolFactory.get(TeamConfig.TOOL_IDS["new_tool"])

# 3. Add to agent
agent = AgentFactory.create(
    name="Agent Name",
    tools=[tavily_tool, new_tool],
    # ... other config
)
```

**Example: Modifying agent instructions**
```python
# Edit the system_prompt in create_search_agent()
system_prompt = """Your updated instructions here..."""
```

## Testing

### Backend Tests

```bash
# Run API integration tests
./scripts/run_e2e_tests.sh

# Or manually with pytest
poetry shell
pytest tests/ -v
```

**Test files:**
- `tests/test_api_integration.py` - API endpoint tests
- `tests/test_entity_processor.py` - Entity processing tests

### Frontend Tests

```bash
cd ui

# Install Playwright (first time only)
npx playwright install chromium

# Run E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test
npm run test:e2e tests/e2e/dashboard.spec.js
```

**Test files:**
- `ui/tests/e2e/dashboard.spec.js` - Dashboard tests
- `ui/tests/e2e/create-team.spec.js` - Team creation tests

### Manual Testing

**Backend:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create team
curl -X POST http://localhost:8000/api/v1/agent-teams \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test topic", "goals": ["Goal 1"]}'

# List teams
curl http://localhost:8000/api/v1/agent-teams
```

**Frontend:**
1. Open http://localhost:5173
2. Click "Create Team"
3. Enter topic and goals
4. Submit and monitor execution

## Code Style

### Python (Backend)

- **Style:** PEP 8
- **Docstrings:** Google style
- **Type hints:** Use for function signatures
- **Imports:** Group by standard lib, third-party, local

**Example:**
```python
def process_entities(
    entities_data: Dict[str, Any],
    topic: str
) -> List[Dict[str, Any]]:
    """
    Process and validate entities from agent response.
    
    Args:
        entities_data: Raw entities from agent
        topic: Research topic
        
    Returns:
        List of validated entity dictionaries
    """
    # Implementation
```

### JavaScript/React (Frontend)

- **Style:** ESLint + Prettier
- **Components:** Functional components with hooks
- **Props:** Destructure in function signature
- **Naming:** PascalCase for components, camelCase for functions

**Example:**
```javascript
function EntityCard({ entity, onExpand }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleClick = () => {
    setIsExpanded(!isExpanded);
    onExpand?.(entity);
  };
  
  return (
    <Card onClick={handleClick}>
      {/* Component content */}
    </Card>
  );
}
```

## Common Issues & Solutions

### CORS Errors

**Problem:** UI shows "Network Error" with CORS in console

**Solution:**
1. Restart backend server
2. Check backend CORS config includes your UI port
3. Verify backend is running: `curl http://localhost:8000/api/v1/health`

### Agent Execution Fails

**Problem:** Team status shows "failed"

**Solution:**
1. Check execution log in UI for error details
2. Verify `AIXPLAIN_API_KEY` in `.env`
3. Check Tavily tool is accessible
4. Review agent configuration in `api/team_config.py`

### Database Issues

**Problem:** SQLite errors or missing data

**Solution:**
1. Check `data/teams.db` exists and is writable
2. Delete database to reset: `rm data/teams.db`
3. Restart backend to recreate tables

### UI Not Updating

**Problem:** UI doesn't show latest data

**Solution:**
1. Check auto-refresh is working (every 3 seconds for running teams)
2. Manually click "Refresh" button
3. Check browser console for errors
4. Verify API is returning correct data: `curl http://localhost:8000/api/v1/agent-teams`

## Adding New Features

### 1. Backend Endpoint

```python
# In api/main.py

@app.get("/api/v1/your-endpoint")
async def your_endpoint():
    """Endpoint description"""
    # Implementation
    return {"data": "response"}
```

### 2. Frontend Component

```javascript
// In ui/src/components/YourComponent.jsx

import { Card } from '@blueprintjs/core';
import './YourComponent.css';

function YourComponent({ prop1, prop2 }) {
  return (
    <Card>
      {/* Component content */}
    </Card>
  );
}

export default YourComponent;
```

### 3. API Client Method

```javascript
// In ui/src/api/client.js

export const agentTeamsAPI = {
  // ... existing methods
  yourMethod: (id) => apiClient.get(`/your-endpoint/${id}`),
};
```

## Debugging

### Backend Debugging

**Enable debug logging:**
```python
# In api/main.py
logging.basicConfig(level=logging.DEBUG)
```

**Check logs:**
- Console output shows all API requests
- Execution logs stored in database
- Agent responses logged to console

### Frontend Debugging

**Browser DevTools:**
- Console: Check for errors and API responses
- Network: Monitor API calls and responses
- React DevTools: Inspect component state

**Vite debugging:**
```bash
# Run with debug output
npm run dev -- --debug
```

## Database Management

### Viewing Data

```bash
# Open SQLite database
sqlite3 data/teams.db

# List tables
.tables

# View teams
SELECT team_id, topic, status FROM teams;

# Exit
.quit
```

### Backup

```bash
# Backup database
cp data/teams.db data/teams.db.backup

# Restore
cp data/teams.db.backup data/teams.db
```

### Reset

```bash
# Delete database (will be recreated on next start)
rm data/teams.db

# Restart backend
python -m api.main
```

## Git Workflow

1. **Create feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and commit:**
```bash
git add .
git commit -m "feat: description of changes"
```

3. **Test before pushing:**
```bash
# Backend tests
./scripts/run_e2e_tests.sh

# Frontend tests
cd ui && npm run test:e2e

# Build check
cd ui && npm run build
```

4. **Push and create PR:**
```bash
git push origin feature/your-feature-name
```

## Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add entity filtering to dashboard
fix: resolve CORS error on team creation
docs: update architecture documentation
refactor: simplify entity processor logic
```

## Getting Help

1. **Check documentation:**
   - `docs/ARCHITECTURE.md` - System architecture
   - `docs/TROUBLESHOOTING.md` - Common issues
   - `README.md` - Quick start guide

2. **Review specs:**
   - `.kiro/specs/osint-agent-team-system/` - Feature specifications

3. **Check tests:**
   - `tests/` - Backend test examples
   - `ui/tests/e2e/` - Frontend test examples

4. **Examine existing code:**
   - Look at similar features for patterns
   - Check component implementations for UI patterns
   - Review API endpoints for backend patterns
