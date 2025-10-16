# Honeycomb OSINT Agent Team System

An OSINT (Open Source Intelligence) Agent Team System designed for the Ministerium für Soziales, Gesundheit und Integration. The system enables policy makers to conduct automated web research on specific topics using aixplain team agents.

## 🚀 Quick Start (From Anywhere)

**Start Backend:**
```bash
./start-backend.sh
```

**Start Frontend:**
```bash
./start-frontend.sh
```

**Access:**
- UI: http://localhost:5173
- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

> **Note:** These scripts work from any directory - they automatically navigate to the correct location.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (Python package manager)
- aixplain API key

### Default Ports

- **Backend API:** `http://localhost:8080`
- **Frontend UI:** `http://localhost:5173`
- **API Documentation:** `http://localhost:8080/docs`

### Initial Setup (First Time Only)

#### 1. Backend Setup

```bash
# Install Python dependencies with Poetry
poetry install

# Configure environment variables
cp .env.example .env
# Edit .env and add your AIXPLAIN_API_KEY and TEAM_API_KEY
```

#### 2. Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Return to root directory
cd ..
```

### Starting the Services

#### Start Backend API (Port 8080)

**Option 1: Using the start script (recommended)**
```bash
./start-backend.sh
```

**Option 2: Manual start**
```bash
# From project root
poetry run python -m api.main

# Or using Poetry shell
poetry shell
python -m api.main

# Or using uvicorn directly
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

The API will be available at:
- **API:** http://localhost:8080
- **API Docs:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/api/v1/health

#### Start Frontend UI (Port 5173)

**Option 1: Using the start script (recommended)**
```bash
./start-frontend.sh
```

**Option 2: Manual start**
```bash
cd ui
npm run dev
```

The UI will be available at http://localhost:5173

### If Ports Are Already in Use

If you already have services running on ports 8080 and 5173, you can either:

**Option A: Stop existing services and restart**
```bash
# Find and kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Then start services using the scripts
./start-backend.sh
./start-frontend.sh
```

**Option B: Use different ports**

For backend (e.g., port 8080):
```bash
# Edit .env file
API_PORT=8080

# Or use environment variable
API_PORT=8080 poetry run python -m api.main
```

For frontend (e.g., port 3000):
```bash
cd ui
npm run dev -- --port 3000
```

Then update UI to connect to new backend port:
```bash
# Create ui/.env.local
echo "VITE_API_BASE_URL=http://localhost:8080" > ui/.env.local

# Restart frontend
npm run dev -- --port 3000
```

## Testing the System

### 0. Manual via UI

* Jugenschutz-Baden-Wuerrtemberg-2025
* Wie ist der Sachstand zum Jugendschutz in Baden-Würrtemberg, welche Stimmen gibt es in der Bevölkerung.

### 1. Run End-to-End Integration Tests

**API Integration Tests (Python/pytest):**
```bash
# Ensure backend is running first, then:
./scripts/run_e2e_tests.sh
```

This will verify:
- Backend API endpoints are working
- CORS is configured correctly for UI
- Data format matches UI expectations
- Full create → list → detail flow works

**UI End-to-End Tests (Playwright):**
```bash
# Ensure BOTH backend AND frontend are running, then:
cd ui
npx playwright install chromium  # First time only
npm run test:e2e
```

This will verify:
- UI loads correctly
- Create team form works end-to-end
- Team list displays correctly
- Navigation between pages works
- Error handling works

**Note:** After making changes to `api/models.py` or `api/main.py`, restart the backend server for changes to take effect.

**Test Status:** ✅ All end-to-end tests passing! See `E2E_TEST_SUCCESS.md` for details.

### 2. Manual Backend API Testing

```bash
# Health check
curl http://localhost:8080/api/v1/health

# Create an agent team
curl -X POST http://localhost:8080/api/v1/agent-teams \
  -H "Content-Type: application/json" \
  -d '{"topic": "Climate policy in Baden-Württemberg", "goals": "Research current initiatives"}'

# List all teams
curl http://localhost:8080/api/v1/agent-teams

# Get team details (replace {team_id} with actual ID)
curl http://localhost:8080/api/v1/agent-teams/{team_id}
```

### 3. Manual Frontend UI Testing

1. Open http://localhost:5174 (or whichever port Vite uses) in your browser
2. Click "Create Team" button
3. Enter a research topic (e.g., "Healthcare policy reforms")
4. Optionally add goals
5. Submit and view the team detail page
6. Monitor execution logs, extracted entities, and generated Sachstand

**Note:** If you see CORS errors, restart the backend server to pick up the latest CORS configuration.

## Port Configuration

### Backend API Port

The backend API runs on port **8080** by default.

**Configuration methods (in order of precedence):**

1. **Environment variable:**
   ```bash
   API_PORT=9000 python -m api.main
   ```

2. **`.env` file:**
   ```bash
   API_PORT=9000
   ```

3. **Command line (uvicorn):**
   ```bash
   uvicorn api.main:app --reload --port 9000
   ```

**Host configuration:**
- Default: `0.0.0.0` (accessible from network)
- Change via `API_HOST` environment variable or `.env` file
- Example: `API_HOST=127.0.0.1` (localhost only)

### Frontend UI Port

The frontend UI runs on port **5173** by default (Vite's default).

**Configuration methods:**

1. **Command line:**
   ```bash
   npm run dev -- --port 3000
   ```

2. **`vite.config.js`:**
   ```javascript
   export default defineConfig({
     plugins: [react()],
     server: {
       port: 3000,
       host: true  // Expose to network
     }
   })
   ```

3. **Package.json script:**
   ```json
   "scripts": {
     "dev": "vite --port 3000"
   }
   ```

### Connecting UI to Custom Backend Port

If you change the backend port, update the UI configuration:

**Option 1: Environment variable (recommended)**

Create `ui/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:9000
```

**Option 2: Edit API client**

Edit `ui/src/api/client.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000';
```

**Note:** After changing `ui/.env.local`, restart the dev server (`npm run dev`).

### CORS Configuration

The backend automatically allows CORS from these ports:
- `http://localhost:5173` (Vite default)
- `http://localhost:5174` (Vite alternate)
- `http://localhost:3000` (Common alternative)

**To add more ports:**

Edit `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:YOUR_PORT",  # Add your port
    ],
    ...
)
```

## Troubleshooting

### CORS Error: "No 'Access-Control-Allow-Origin' header"

**Problem:** UI shows "Failed to load agent teams: Network Error" and browser console shows CORS error.

**Solution:**
1. Restart the backend server (Ctrl+C and run `uvicorn api.main:app --reload --port 8080` again)
2. The backend CORS config includes ports 5173, 5174, and 3000
3. Check that backend is running: `curl http://localhost:8080/api/v1/health`

### Backend Not Starting

**Problem:** Backend fails to start or shows import errors.

**Solution:**
1. Ensure you're in the poetry shell: `poetry shell`
2. Check dependencies are installed: `poetry install`
3. Verify `.env` file exists with `AIXPLAIN_API_KEY`

### UI Not Loading

**Problem:** UI shows blank page or won't start.

**Solution:**
1. Check Node.js version: `node --version` (needs 18+)
2. Reinstall dependencies: `cd ui && npm install`
3. Clear Vite cache: `rm -rf ui/node_modules/.vite`

## Project Structure

```
.
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   ├── models.py          # Data models
│   ├── persistent_storage.py  # SQLite storage
│   ├── services/          # Business logic
│   └── routes/            # API endpoints
├── ui/                    # React monitoring UI
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── pages/        # Dashboard, TeamDetail
│   │   └── components/   # CreateTeamModal
│   └── package.json
├── data/                  # SQLite database (created automatically)
│   └── teams.db          # Persistent storage
├── tests/                 # Test files
├── output/               # Generated JSON-LD files
└── pyproject.toml        # Python dependencies
```

## Data Persistence

The system uses **SQLite** for persistent storage of agent teams and execution history.

- **Database location:** `./data/teams.db` (created automatically)
- **What's stored:** Team metadata, execution logs, agent responses, JSON-LD output
- **Survives restarts:** Yes, all data persists across backend restarts
- **Backup:** Simply copy the `data/teams.db` file

**To change database location:**
```bash
# In .env file
DB_PATH=./custom/path/teams.db

# Or environment variable
DB_PATH=/var/lib/honeycomb/teams.db python -m api.main
```

## Current Implementation Status

See `.kiro/specs/osint-agent-team-system/tasks.md` for detailed task completion status.

**Completed:**
- ✓ Core data models and validation
- ✓ In-memory storage with repository pattern
- ✓ REST API endpoints (create, list, get team)
- ✓ Health check endpoint
- ✓ React monitoring UI with dashboard and detail views

**In Progress:**
- Agent team orchestration with aixplain
- OSINT web research capabilities
- Entity extraction and JSON-LD generation

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design, agent coordination, and data flow
- **[Known Issues](KNOWN_ISSUES.md)** - Resolved issues, current limitations, and debugging tips
- **[Contributing](docs/CONTRIBUTING.md)** - Development setup, workflow, and code style

## License

Internal use for Ministerium für Soziales, Gesundheit und Integration Baden-Württemberg.
