# Changelog: Model Configuration and Run Metadata

## Summary
Added tracking of model, duration, and git version information for each agent team run.

## Changes Made

### 1. Model Configuration Update
- **Changed from:** GPT-4o (`6646261c6eb563165658bbb1`)
- **Changed to:** GPT OSS 120b (`6895f768d50c89537c1cf24e`)
- **Affected agents:** All agents (Mentalist, Inspector, Orchestrator, Feedback Combiner, Response Generator, Search Agent, Wikipedia Agent)
- **Files modified:**
  - `api/config.py` - Updated model IDs and defaults
  - `api/main.py` - Updated display name in API response

### 2. Database Schema Updates
Added new columns to the `teams` table:
- `model_id` (TEXT) - The model ID used for the run
- `model_name` (TEXT) - Human-readable model name (e.g., "GPT OSS 120b")
- `duration_seconds` (REAL) - Total execution time in seconds
- `git_sha` (TEXT) - Git commit SHA at time of run
- `git_repo_url` (TEXT) - Repository URL for linking to commit

**File:** `api/persistent_storage.py`

### 3. Backend API Changes

#### Git Information Capture
Added `get_git_info()` function to capture:
- Current commit SHA using `git rev-parse HEAD`
- Remote repository URL using `git config --get remote.origin.url`
- Automatic conversion of SSH URLs to HTTPS format

#### Team Creation
Updated `create_team()` to accept and store:
- `model_id` - Captured from `Config.TEAM_AGENT_MODEL`
- `model_name` - Human-readable name
- `git_sha` - Current commit hash
- `git_repo_url` - Repository URL

#### Duration Tracking
Updated `update_team_status()` to automatically calculate duration when a team completes or fails:
- Calculates time difference between `created_at` and completion time
- Stores in `duration_seconds` field

**Files:** `api/main.py`, `api/persistent_storage.py`

### 4. Frontend UI Updates

#### Dashboard Table
Added three new columns to the teams list:
1. **Model** - Displays the model name used (e.g., "GPT OSS 120b")
2. **Duration** - Shows execution time in human-readable format (e.g., "45s", "2m", "1h")
3. **Version** - Git SHA with clickable link to commit on GitHub/GitLab

#### Styling
Added CSS for new columns:
- `.model-cell` - Centered model tag display
- `.duration-cell` - Monospace font for duration
- `.version-cell` - Styled links to git commits

**Files:** `ui/src/pages/Dashboard.jsx`, `ui/src/pages/Dashboard.css`

### 5. Frontend Configuration Cleanup
Removed all hardcoded fallback data from `TeamConfigInfo.jsx`:
- Component now exclusively uses API data
- Shows error message if API is unavailable (no stale fallback data)
- All configuration comes from backend

**File:** `ui/src/components/TeamConfigInfo.jsx`

## Migration Notes

### Database Migration
The schema changes are backward compatible:
- New columns are added automatically on startup
- Existing rows will have `NULL` values for new fields
- No data loss occurs

### Existing Teams
Teams created before this update will show:
- Model: `-` (not tracked)
- Duration: `-` (not tracked)
- Version: `-` (not tracked)

New teams will have all fields populated.

## Testing

To verify the changes:

1. **Backend:**
   ```bash
   # Check git info is captured
   python -c "from api.main import get_git_info; print(get_git_info())"
   
   # Start the API
   cd api && python main.py
   ```

2. **Frontend:**
   ```bash
   # Start the UI
   cd ui && npm run dev
   ```

3. **Create a test team:**
   - Navigate to the dashboard
   - Click "Create Team"
   - Submit a research topic
   - Verify the new columns appear in the table

4. **Verify git link:**
   - Click on the git SHA in the Version column
   - Should open the commit on GitHub/GitLab

## Configuration Reference

### Current Model Configuration
```python
# api/config.py
GPT_OSS_120B = "6895f768d50c89537c1cf24e"
SEARCH_AGENT_MODEL = GPT_OSS_120B
WIKIPEDIA_AGENT_MODEL = GPT_OSS_120B
TEAM_AGENT_MODEL = GPT_OSS_120B
```

### API Response Format
```json
{
  "team_id": "abc123...",
  "topic": "Research topic",
  "status": "completed",
  "model_id": "6895f768d50c89537c1cf24e",
  "model_name": "GPT OSS 120b",
  "duration_seconds": 45.3,
  "git_sha": "a1b2c3d4e5f6...",
  "git_repo_url": "https://github.com/user/repo",
  "created_at": "2025-10-15T10:30:00Z",
  "updated_at": "2025-10-15T10:30:45Z"
}
```

## Benefits

1. **Reproducibility:** Know exactly which model and code version produced each result
2. **Performance Tracking:** Monitor execution times across runs
3. **Debugging:** Quickly identify which code version caused issues
4. **Cost Analysis:** Track model usage for cost optimization
5. **Audit Trail:** Complete history of what ran when and with what configuration
