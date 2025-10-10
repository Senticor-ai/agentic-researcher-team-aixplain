# Quick Start Guide

Get the Honeycomb OSINT Agent Team System running in 5 minutes.

## Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (install: `curl -sSL https://install.python-poetry.org | python3 -`)
- aixplain API key

## Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
cd honeycomb-osint-agent-team-system

# Copy environment file
cp .env.example .env
```

## Step 2: Configure API Key

Edit `.env` and add your aixplain API key:
```bash
AIXPLAIN_API_KEY=your_actual_api_key_here
```

## Step 3: Start Backend (Terminal 1)

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Start backend API
python -m api.main
```

✅ Backend running at: **http://localhost:8000**
📚 API docs at: **http://localhost:8000/docs**

## Step 4: Start Frontend (Terminal 2)

```bash
# Navigate to UI directory
cd ui

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

## Step 5: Test the System

1. Open **http://localhost:5173** in your browser
2. Click **"Create Team"** button
3. Enter a research topic (e.g., "Jugendschutz Baden-Württemberg 2025")
4. Click **"Create Team"**
5. Watch the real-time monitoring as the team executes!

**Note:** All teams are saved to `./data/teams.db` and will persist across restarts!

## Default Ports

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Frontend UI | 5173 | http://localhost:5173 |

## Change Ports (Optional)

### Backend Port

**Option 1: Environment variable**
```bash
API_PORT=9000 python -m api.main
```

**Option 2: Edit .env file**
```bash
API_PORT=9000
```

### Frontend Port

```bash
npm run dev -- --port 3000
```

### Connect UI to Different Backend Port

Create `ui/.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:9000
```

Then restart: `npm run dev`

## Verify Everything Works

### Check Backend
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy",...}
```

### Check Frontend
Open http://localhost:5173 in your browser

## Troubleshooting

### Port Already in Use

**Backend:**
```bash
# Use different port
API_PORT=8001 python -m api.main
```

**Frontend:**
```bash
# Vite will auto-try next port (5174, 5175, etc.)
npm run dev
```

### CORS Error

1. Restart backend server
2. Check frontend port is 5173, 5174, or 3000
3. Clear browser cache

### Backend Won't Start

1. Check you're in poetry shell: `poetry shell`
2. Verify .env file exists with API key
3. Check dependencies: `poetry install`

### Frontend Won't Start

1. Check Node.js version: `node --version` (needs 18+)
2. Reinstall: `rm -rf node_modules && npm install`
3. Clear cache: `rm -rf node_modules/.vite`

## What's Next?

- Read the full [README.md](README.md) for detailed information
- Check [docs/PORT_CONFIGURATION.md](docs/PORT_CONFIGURATION.md) for advanced port setup
- Review [docs/UI_MONITORING_GUIDE.md](docs/UI_MONITORING_GUIDE.md) to understand the monitoring features
- See [docs/EXECUTION_STATS_IMPLEMENTATION.md](docs/EXECUTION_STATS_IMPLEMENTATION.md) for execution statistics

## Example Research Topics

Try these topics to test the system:

1. **"Jugendschutz Baden-Württemberg 2025"**
   - Goals: "Find organizations working on youth protection"

2. **"Climate policy in Baden-Württemberg"**
   - Goals: "Research current initiatives and stakeholders"

3. **"Healthcare reforms Germany 2025"**
   - Goals: "Identify key policy makers and organizations"

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [docs/](docs/) folder for guides
- Check backend logs for errors
- Check browser console for frontend errors

---

**Ready to go!** 🚀

Open http://localhost:5173 and start creating agent teams!
