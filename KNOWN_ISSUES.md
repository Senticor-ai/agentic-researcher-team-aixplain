# Known Issues and Resolutions

This document tracks known issues, their resolutions, and current limitations of the Honeycomb OSINT Agent Team System.

## ✅ Resolved Issues

### 1. Mentalist Self-Assignment Bug (Oct 15, 2025)

**Issue:** Mentalist was assigning tasks to itself instead of to the Search Agent, causing research to fail with 0 entities extracted.

**Root Cause:** When analyzing complex topics, the Mentalist would create a task "Create MECE decomposition" assigned to "Mentalist" (itself). The Orchestrator would call Mentalist again, but MECE decomposition is conceptual planning, not an executable task.

**Resolution:** Updated `api/instructions/mentalist.py` with explicit warnings:
- MECE decomposition is INTERNAL planning, not a delegated task
- NEVER assign tasks to "Mentalist"
- ALWAYS assign search tasks to "Search Agent"
- Added example workflows showing correct vs incorrect patterns

**Evidence:**
- Failing run: 0 Search Agent calls, 0 entities
- After fix: Multiple Search Agent calls, entities extracted successfully

**Files:** `api/instructions/mentalist.py`

---

### 2. Claude Sonnet 4 Incompatibility (Oct 2025)

**Issue:** When using Claude Sonnet 4 as the team model, the Mentalist would return empty arrays `[]` instead of creating tasks.

**Root Cause:** Claude Sonnet 4 has different instruction-following behavior compared to GPT-4o. It was too conservative and wouldn't create tasks without explicit examples.

**Resolution:** 
- Switched back to GPT-4o for all agents (Mentalist, Inspector, Orchestrator, Response Generator)
- GPT-4o provides better instruction following and more reliable task creation
- Documented model compatibility in configuration

**Current Configuration:**
- Team agents: GPT-4o (`6646261c6eb563165658bbb1`)
- Search Agent: GPT-4o (`6646261c6eb563165658bbb1`)
- Wikipedia Agent: GPT-4o (`6646261c6eb563165658bbb1`)

**Files:** `api/config.py`, `api/team_config.py`

---

### 3. KeyError in Production Stats (Oct 2025)

**Issue:** Production deployment crashed with `KeyError: 'apiCalls'` when trying to display execution statistics.

**Root Cause:** The `executionStats` object from aixplain API doesn't always include all expected fields. Some fields may be missing depending on the execution context.

**Resolution:** Added defensive programming with `.get()` method and default values:
```python
api_calls = execution_stats.get('apiCalls', 'N/A')
runtime = execution_stats.get('runtime', 'N/A')
credits = execution_stats.get('credits', 'N/A')
```

**Files:** `api/main.py`

---

### 4. Config Refactor (Oct 2025)

**Issue:** Configuration was scattered across multiple files, making it hard to manage API keys, model IDs, and tool IDs.

**Resolution:** Centralized all configuration in `api/config.py`:
- Single source of truth for all IDs
- Environment variable management
- Clear separation of testing vs production configs
- Helper methods for accessing configuration

**Files:** `api/config.py`, `api/team_config.py`

---

## ⚠️ Current Limitations

### 1. Limited Entity Types

**Status:** By design

Currently extracts only:
- Person entities (with roles, descriptions, sources)
- Organization entities (with descriptions, sources)

Future enhancements may include:
- Topic entities (themes, policy areas)
- Event entities (conferences, deadlines)
- Policy entities (laws, regulations)

---

### 2. No Entity Deduplication

**Status:** Planned enhancement

The system may extract duplicate entities if they appear in multiple search results with slightly different names or descriptions.

**Workaround:** Manual review of extracted entities

**Future:** Implement entity deduplication using:
- Wikidata IDs (when Wikipedia tool is enabled)
- Name similarity matching
- URL comparison

---

### 3. Search Tool Limitations

**Status:** External dependency

**Tavily Search:**
- Rate limits apply based on API plan
- May timeout on complex queries
- Coverage varies by topic and language

**Workaround:** 
- System includes fallback strategies
- Alternative search terms are tried automatically
- Multiple search rounds for comprehensive coverage

---

### 4. German Language Support

**Status:** Partial support

The system works with German topics but:
- Search results quality varies
- Some German government sites may not be well-indexed
- Entity extraction works but may miss nuances

**Workaround:**
- Use Google Search tool for German topics (better .de domain coverage)
- Provide alternative search terms in German
- Manual review of extracted entities

---

### 5. No Real-time Updates

**Status:** By design

The UI polls for updates every 3 seconds. There's no WebSocket or Server-Sent Events for real-time updates.

**Impact:** Minimal - 3-second delay is acceptable for research tasks that take minutes

**Future:** Could implement WebSockets if needed

---

## 🔍 Debugging Tips

### Issue: No Entities Extracted

**Check:**
1. Execution log for errors
2. Intermediate steps - was Search Agent called?
3. First task assignment - is it assigned to "Search Agent"?
4. Search results - did Tavily return results?

**Common Causes:**
- Mentalist assigning tasks to itself (see resolved issue #1)
- Search tool timeout or rate limit
- Topic too specific or obscure

---

### Issue: Fabricated Entities

**Check:**
1. Source URLs - are they real or placeholders?
2. Execution log - did Search Agent actually search?
3. Entity descriptions - are they generic or specific?

**Common Causes:**
- Response Generator creating entities without real searches
- Search Agent returning empty results
- Mentalist not calling Search Agent

---

### Issue: CORS Errors

**Check:**
1. Backend is running on correct port (8080)
2. Frontend is running on allowed port (5173, 5174, or 3000)
3. Backend was restarted after CORS config changes

**Resolution:**
```bash
# Restart backend
./start-backend.sh

# Check health
curl http://localhost:8080/api/v1/health
```

---

## 📝 Reporting New Issues

When reporting issues, please include:

1. **Team ID** - From the URL or API response
2. **Topic** - The research topic used
3. **Execution Log** - From the team detail page
4. **Expected vs Actual** - What you expected vs what happened
5. **Steps to Reproduce** - How to recreate the issue

**Where to report:**
- Internal issue tracker
- Or create a markdown file in the project root with details

---

## 🔄 Version History

- **v0.1.0** (Oct 2025) - Initial release
  - Core functionality working
  - Known issues documented
  - GPT-4o as default model
