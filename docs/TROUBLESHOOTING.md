# Troubleshooting Guide

## Common Issues

### CORS Errors

**Symptom:** UI shows "Failed to load agent teams: Network Error" and browser console shows CORS error.

**Cause:** Backend CORS configuration not allowing UI origin.

**Solution:**
1. Restart the backend server (Ctrl+C and run `python -m api.main` again)
2. Verify backend is running: `curl http://localhost:8000/api/v1/health`
3. Check UI port matches CORS config in `api/main.py` (5173, 5174, or 3000)
4. If using custom port, add it to CORS origins in `api/main.py`

### Agent Execution Fails

**Symptom:** Team status shows "failed" in UI.

**Possible Causes:**
1. **API Key Issues:** Invalid or missing aixplain API key
2. **Tool Access:** Tavily Search tool not accessible
3. **Network Issues:** Timeout or connection problems
4. **Configuration:** Agent configuration errors

**Solution:**
1. Check execution log in UI for specific error messages
2. Verify `.env` file has valid `AIXPLAIN_API_KEY`
3. Test API key: Create a simple team with a well-known topic
4. Check agent configuration in `api/team_config.py`
5. Review Tavily tool ID is correct

### No Entities Extracted

**Symptom:** Team completes but sachstand has empty `hasPart` array.

**Possible Causes:**
1. **Topic Too Specific:** No information available online
2. **Search Results:** Tavily returned no relevant results
3. **Parsing Issues:** Agent output format not recognized
4. **Entity Criteria:** No entities met extraction criteria

**Solution:**
1. Try a broader, more well-known topic
2. Check execution log for search results
3. Review agent trace to see what Search Agent returned
4. Test with known topics (e.g., "Climate policy Germany")

### Backend Won't Start

**Symptom:** Backend fails to start or shows import errors.

**Solution:**
1. Ensure you're in poetry shell: `poetry shell`
2. Install dependencies: `poetry install`
3. Check Python version: `python --version` (needs 3.12+)
4. Verify `.env` file exists with `AIXPLAIN_API_KEY`
5. Check for port conflicts: `lsof -i :8000`

### UI Won't Load

**Symptom:** UI shows blank page or won't start.

**Solution:**
1. Check Node.js version: `node --version` (needs 18+)
2. Reinstall dependencies: `cd ui && rm -rf node_modules && npm install`
3. Clear Vite cache: `rm -rf ui/node_modules/.vite`
4. Check for port conflicts: `lsof -i :5173`
5. Try different port: `npm run dev -- --port 3000`

### Database Errors

**Symptom:** SQLite errors or data not persisting.

**Solution:**
1. Check `data/` directory exists and is writable
2. Verify `data/teams.db` file permissions
3. Reset database: `rm data/teams.db` (will be recreated)
4. Check `DB_PATH` environment variable if using custom location

### UI Not Updating

**Symptom:** UI doesn't show latest team status or data.

**Solution:**
1. Check auto-refresh is working (every 3 seconds for running teams)
2. Click "Refresh" button manually
3. Check browser console for errors
4. Verify API returns correct data: `curl http://localhost:8000/api/v1/agent-teams/{team_id}`
5. Clear browser cache and reload

### Port Conflicts

**Symptom:** "Address already in use" error.

**Backend:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
API_PORT=9000 python -m api.main
```

**Frontend:**
```bash
# Find process using port 5173
lsof -i :5173

# Kill process
kill -9 <PID>

# Or use different port
npm run dev -- --port 3000
```

### Tests Failing

**Backend tests:**
```bash
# Ensure backend is running first
python -m api.main

# In another terminal
./scripts/run_e2e_tests.sh
```

**Frontend tests:**
```bash
# Ensure BOTH backend AND frontend are running
python -m api.main  # Terminal 1
cd ui && npm run dev  # Terminal 2

# In another terminal
cd ui && npm run test:e2e
```

## Debugging Tips

### Backend Debugging

**Enable verbose logging:**
```python
# In api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check execution logs:**
- View in UI team detail page
- Query database: `sqlite3 data/teams.db "SELECT execution_log FROM teams WHERE team_id='...'"`

**Test API directly:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create team
curl -X POST http://localhost:8000/api/v1/agent-teams \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test", "goals": ["Goal 1"]}'

# Get team
curl http://localhost:8000/api/v1/agent-teams/{team_id}
```

### Frontend Debugging

**Browser DevTools:**
- **Console:** Check for JavaScript errors
- **Network:** Monitor API calls and responses
- **React DevTools:** Inspect component state

**Check API connection:**
```javascript
// In browser console
fetch('http://localhost:8000/api/v1/health')
  .then(r => r.json())
  .then(console.log)
```

### Agent Debugging

**Check agent response:**
```bash
# Query database for agent response
sqlite3 data/teams.db "SELECT agent_response FROM teams WHERE team_id='...'"
```

**Review trace:**
- Open team detail page in UI
- Expand "Agent Execution Trace" section
- Check each step for errors or unexpected behavior

**Test agent configuration:**
```python
# In Python shell
from api.team_config import TeamConfig

# Create test team
team = TeamConfig.create_team("Test topic", ["Goal 1"], model="testing")
print(f"Team ID: {team.id}")

# Run test
response = team.run("Research test topic")
print(response.data.output)
```

## Performance Issues

### Slow Team Execution

**Possible Causes:**
1. Complex topic requiring many searches
2. Interaction limit too high
3. Network latency to aixplain/Tavily

**Solution:**
1. Reduce interaction limit (default: 50)
2. Use more specific topics
3. Check network connection
4. Monitor execution stats in UI

### UI Slow to Load

**Possible Causes:**
1. Large number of teams in database
2. Large execution logs
3. Network latency to backend

**Solution:**
1. Implement pagination (future enhancement)
2. Limit log display in UI
3. Use local backend (not remote)

## Data Issues

### Missing Sachstand

**Symptom:** Team completed but no sachstand available.

**Solution:**
1. Check team status is "completed" not "failed"
2. Review execution log for errors
3. Check `output/` directory for JSON-LD file
4. Query database: `sqlite3 data/teams.db "SELECT sachstand FROM teams WHERE team_id='...'"`

### Corrupted Database

**Symptom:** SQLite errors or inconsistent data.

**Solution:**
1. Backup current database: `cp data/teams.db data/teams.db.backup`
2. Try to repair: `sqlite3 data/teams.db "PRAGMA integrity_check;"`
3. If corrupted, delete and recreate: `rm data/teams.db`
4. Restore from backup if available

## Getting More Help

1. **Check logs:**
   - Backend console output
   - Browser console (F12)
   - Execution logs in UI

2. **Review documentation:**
   - `docs/ARCHITECTURE.md` - System design
   - `docs/CONTRIBUTING.md` - Development guide
   - `README.md` - Quick start

3. **Test with known working examples:**
   - Use test topics from `tests/` directory
   - Try simple topics like "Climate policy Germany"

4. **Isolate the problem:**
   - Test backend API directly with curl
   - Test frontend with mock data
   - Test agent configuration separately
