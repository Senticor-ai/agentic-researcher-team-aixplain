# End-to-End Testing Guide

## Overview

This directory contains end-to-end tests for the Honeycomb OSINT Agent Team System, including a specific test case for researching "Lagebericht zur Kinderarmut in Baden-Württemberg" (Child Poverty Report in Baden-Württemberg).

## Test Files

### 1. Manual Configuration Test
**File:** `manual_test_agent.py`

Tests agent configuration without requiring API key or server:
- Verifies agent configuration module imports
- Creates walking skeleton configuration
- Formats research prompts

**Run:**
```bash
python tests/manual_test_agent.py
```

**Expected Output:** ✅ All configuration tests pass

---

### 2. End-to-End Kinderarmut Test
**File:** `e2e_test_kinderarmut.py`

Full integration test that:
1. Creates an agent team for researching child poverty stakeholders
2. Waits for agent execution (up to 120 seconds)
3. Retrieves and analyzes results
4. Saves results to JSON file

**Prerequisites:**
- Valid `AIXPLAIN_API_KEY` in `.env` file
- API server running on `http://localhost:8000`

**Run:**
```bash
# Terminal 1: Start API server
poetry run python api/main.py

# Terminal 2: Run E2E test
python tests/e2e_test_kinderarmut.py
```

**Expected Output:**
- ✅ Agent team created
- ⏳ Status updates (pending → running → completed)
- 📊 Results analysis with agent response
- 💾 Results saved to `tests/e2e_results_kinderarmut.json`

---

### 3. Expected Honeycomb Structure
**File:** `expected_honeycomb_kinderarmut.json`

Defines the expected JSON-LD structure for the research output:

```json
{
  "@context": "https://schema.org",
  "@type": "ResearchProject",
  "name": "Lagebericht zur Kinderarmut in Baden-Württemberg",
  "stakeholders": {
    "organizations": [...],
    "persons": [...]
  },
  "sources": [...]
}
```

This structure includes:
- **Known sources:** Ministry websites, federal publications
- **To be discovered:** NGOs, press organizations, think tanks
- **Key stakeholders:** Government officials, experts, organizations

---

## Setup Instructions

### 1. Get aixplain API Key

1. Sign up at [aixplain.com](https://aixplain.com)
2. Navigate to API settings
3. Generate an API key

### 2. Configure Environment

Edit `.env` file in project root:
```bash
AIXPLAIN_API_KEY=your_actual_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Verify Configuration

```bash
python tests/manual_test_agent.py
```

Should show: ✅ All tests pass

---

## Running the E2E Test

### Step 1: Start API Server

```bash
poetry run python api/main.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Run E2E Test

In a new terminal:
```bash
python tests/e2e_test_kinderarmut.py
```

### Step 3: Monitor Progress

The test will:
1. ✅ Check API key configuration
2. ✅ Verify API server is running
3. 📝 Create agent team
4. ⏳ Poll status every 5 seconds
5. 📊 Display results when complete

### Step 4: Review Results

Check the output files:
- `tests/e2e_results_kinderarmut.json` - Full agent response
- `tests/expected_honeycomb_kinderarmut.json` - Expected structure

---

## Test Case: Kinderarmut Research

### Research Topic
"Lagebericht zur Kinderarmut in Baden-Württemberg"

### Research Goals
1. Identify NGOs working on child poverty in Baden-Württemberg
2. Find press organizations covering child poverty issues
3. Discover think tanks researching child poverty
4. Locate relevant federal and state publications
5. Extract key stakeholder organizations and contacts

### Known Sources
- **Ministry:** Ministerium für Soziales, Gesundheit und Integration BW
- **Federal:** Bundesministerium für Familie, Senioren, Frauen und Jugend
- **Statistics:** Statistisches Landesamt Baden-Württemberg

### Expected Discoveries
- NGOs working on child poverty
- Press organizations covering social issues
- Think tanks researching poverty
- Key experts and officials
- Relevant publications and reports

---

## Troubleshooting

### API Key Issues

**Error:** `AIXPLAIN_API_KEY not configured`

**Solution:**
1. Check `.env` file exists in project root
2. Verify API key is not the placeholder value
3. Restart API server after updating `.env`

### Server Not Running

**Error:** `API server not running at http://localhost:8000`

**Solution:**
```bash
# Start server in separate terminal
poetry run python api/main.py
```

### Agent Execution Timeout

**Error:** `Timeout: Agent did not complete within 120s`

**Possible causes:**
- Network issues
- aixplain API rate limits
- Complex research taking longer than expected

**Solution:**
- Check execution log in results file
- Increase `MAX_WAIT_TIME` in test script
- Verify aixplain API status

### Import Errors

**Error:** `Functions could not be loaded`

**Solution:**
- This is expected without valid API key
- Set valid `AIXPLAIN_API_KEY` in `.env`
- Restart Python process

---

## Understanding Results

### Agent Response Structure

```json
{
  "team_id": "uuid",
  "topic": "Research topic",
  "status": "completed",
  "agent_response": {
    "agent_id": "aixplain-agent-id",
    "status": "completed",
    "output": "Agent's research findings..."
  },
  "execution_log": [
    "Starting agent creation...",
    "Agent created with ID: ...",
    "Running agent...",
    "Agent completed successfully"
  ]
}
```

### Status Values

- `pending` - Team created, agent not started yet
- `running` - Agent is executing research
- `completed` - Agent finished successfully
- `failed` - Agent execution failed (check logs)

### Execution Log

The log shows:
1. Agent creation start
2. Agent ID assignment
3. Research execution start
4. Completion or error messages

---

## Next Steps

After successful E2E test:

1. **Review Results:** Check if agent found relevant stakeholders
2. **Validate Output:** Compare with expected honeycomb structure
3. **Iterate:** Refine prompts or goals based on results
4. **Implement Task 4:** Add entity extraction and JSON-LD formatting
5. **Build UI:** Create monitoring interface (Task 5)

---

## Support

For issues:
1. Check execution logs in results JSON
2. Verify API server logs
3. Test with simpler topics first
4. Consult aixplain documentation: https://docs.aixplain.com/

---

## Example Output

Successful test output:
```
============================================================
End-to-End Test: Kinderarmut Research
============================================================
✅ API key configured: sk-1234567...
✅ API server is running

📝 Creating agent team for Kinderarmut research...
   Topic: Lagebericht zur Kinderarmut in Baden-Württemberg
   Goals: 5 research objectives
✅ Agent team created: 550e8400-e29b-41d4-a716-446655440000
   Status: pending

⏳ Polling team status (max 120s)...
   [0s] Status: pending
   [5s] Status: running
      📋 Starting agent creation for topic: ...
      📋 Agent created with ID: agent-123
      📋 Running agent with research prompt
   [45s] Status: completed
✅ Agent execution completed!

📊 Results Analysis:
============================================================
Team ID: 550e8400-e29b-41d4-a716-446655440000
Status: completed

🤖 Agent Response:
   Output: Based on my research, I found the following...

💾 Full results saved to: tests/e2e_results_kinderarmut.json

✅ End-to-end test PASSED
```
