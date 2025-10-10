# Implementation Plan

## Technology Stack

- **Backend**: Python 3.12 with FastAPI
- **Package Management**: Poetry
- **Agent Framework**: aixplain Python SDK (https://docs.aixplain.com/api-reference/python/)
- **Key Dependencies**:
  - `aixplain` - Python SDK for agent creation and management
  - `fastapi` - API framework
  - `uvicorn` - ASGI server
  - `pydantic` - Data validation
  - `python-dotenv` - Environment configuration

## aixplain SDK Key Concepts

- **Agent Creation**: Use `aixplain.Agent.create()` to create individual agents
- **Team Agents**: Use `aixplain.TeamAgent.create()` for multi-agent teams with Mentalist, Inspector, and Orchestrator
- **Tools**: Add tools using `aixplain.Tool` - authentication handled by aixplain
- **Shared Memory**: Team agents have built-in shared memory for coordination
- **Running Agents**: Use `agent.run(input)` to execute agents synchronously or asynchronously
- **CRITICAL: Mentalist vs WorkflowTask**: When `use_mentalist=True`, DO NOT use `WorkflowTask` on agents. WorkflowTask takes planning responsibility away from Mentalist, causing conflicts. Let Mentalist plan dynamically based on instructions instead.

## Current Implementation Status

### ✅ Completed (Phase 1)
- Full API implementation with all endpoints
- Team agent configuration with built-in micro agents (Mentalist, Inspector, Orchestrator, Response Generator)
- Search Agent with Tavily tool for entity extraction
- Entity processing and JSON-LD Sachstand generation
- Complete UI with dashboard, team creation, and detail views
- End-to-end testing infrastructure
- Working entity extraction for simple topics

### 🚧 Current Status
The system is fully functional with:
- Complete API with all core endpoints
- Team agent configuration with Mentalist, Inspector, Orchestrator, Response Generator
- Search Agent with Tavily tool for entity extraction
- Wikipedia Agent for entity enrichment (optional)
- Full UI with real-time monitoring, execution trace, and stats
- Entity processing and JSON-LD Sachstand generation
- Fallback strategies for complex topics
- End-to-end testing infrastructure

### 📋 Recommended Next Steps (Phase 4)
1. **Enhance execution stats display** (Task 19)
   - Add execution stats overview to dashboard
   - Improve stats display in team detail with charts
   - Add real-time cost monitoring
   - Export execution stats for analysis
2. **Improve entity extraction quality** (Task 20)
   - Analyze extraction patterns from real-world usage
   - Refine agent prompts based on findings
   - Add entity validation and quality checks
   - Implement entity deduplication
3. **Add Google Search as backup** (Task 21)
   - Configure Google Search tool alongside Tavily
   - Test with topics that failed with Tavily only
4. **Enhance UI with better guidance** (Task 22)
   - Add topic validation and suggestions
   - Improve error messages and troubleshooting
   - Add entity quality indicators
5. **Performance optimization** (Task 23)
   - Add execution time and cost tracking
   - Implement caching for repeated topics
   - Optimize agent configuration for cost

### 🔮 Future Enhancements (Optional)
- **Phase 5**: Firecrawl for deep website crawling (Task 24)
- **Phase 6**: MECE decomposition and advanced strategy (Tasks 25-26)
- **Phase 7**: Evaluation suite and production deployment (Tasks 27-28)

## Phase 1: Walking Skeleton - Simple Topic Research (COMPLETED)

- [x] 1. Set up project structure and development environment
  - Create project directory structure (api/, ui/, tests/, output/, config/)
  - Initialize Python project with Poetry (`poetry init`)
  - Add dependencies: aixplain, fastapi, uvicorn, pydantic, python-dotenv, websockets
  - Set up .env file with AIXPLAIN_API_KEY placeholder
  - Create .gitignore for sensitive files (.env, __pycache__, .venv, output/)
  - _Requirements: 1.1, 9.1_

- [x] 2. Implement minimal Management API
  - [x] 2.1 Create FastAPI application with basic configuration
    - Set up FastAPI server with CORS for UI (port 8000)
    - Load configuration from config.yaml and .env using python-dotenv
    - Implement health check endpoint GET /api/v1/health
    - Create main.py with uvicorn server setup
    - _Requirements: 1.1_

  - [x] 2.2 Implement POST /api/v1/agent-teams endpoint
    - Accept topic and goals in request body
    - Generate unique team_id
    - Return team_id and status "pending"
    - Store team metadata in memory (dict/map)
    - _Requirements: 1.1_

  - [x] 2.3 Implement GET /api/v1/agent-teams endpoint
    - Return list of all teams with status
    - Include team_id, topic, status, created_at
    - _Requirements: 1.2_

  - [x] 2.4 Implement GET /api/v1/agent-teams/{team_id} endpoint
    - Return detailed team information
    - Include topic, goals, status, execution_log
    - _Requirements: 1.2_

  - [x] 2.5 Implement GET /api/v1/sachstand/{team_id} endpoint
    - Return JSON-LD Sachstand for completed team
    - Include file path and content
    - _Requirements: 1.2, 6.4_

- [x] 3. Integrate with aixplain Team Agents API
  - [x] 3.1 Create aixplain client module using Python SDK
    - Install aixplain SDK: `poetry add aixplain`
    - Import aixplain and initialize with API key from .env
    - Create AgentClient class wrapping aixplain SDK
    - Implement function to create agent using aixplain.Agent.create()
    - Implement function to run agent using agent.run()
    - Handle API errors with retries and logging
    - _Requirements: 1.1_

  - [x] 3.2 Configure team agent with built-in micro agents (walking skeleton V2)
    - Use aixplain SDK TeamAgentFactory to create team
    - Built-in micro agents (automatic): Mentalist, Inspector, Orchestrator, Response Generator
    - Define Search Agent (user-defined) with Tavily Search tool
    - Set instructions for Mentalist (simple strategy, no MECE)
    - Enable Inspector to review output (inspector_targets=["output"])
    - Set model (e.g., "gpt-4o-mini" for testing) for micro agents
    - _Requirements: 1.1, 3.1_

  - [x] 3.3 Implement team spawning in POST /api/v1/agent-teams
    - Call aixplain SDK: team = TeamAgentFactory.create(...)
    - Parameters:
      - name: Team name
      - instructions: Instructions for Mentalist
      - agents: [search_agent] (user-defined agents list)
      - use_mentalist: True
      - use_inspector: True
      - inspector_targets: ["output"]
      - llm_id: Model ID for micro agents
    - Run team asynchronously: response = team.run(topic)
    - Store team_id mapping (aixplain_team_id)
    - Update team status to "running"
    - _Requirements: 1.1_

- [x] 4. Implement entity extraction and JSON-LD output with core team
  - [x] 4.1 Define schema.org entity structure
    - Create Entity data model (Person, Organization)
    - Define JSON-LD Sachstand output structure with @context
    - Include basic properties (name, description, url, sources)
    - _Requirements: 4.1, 4.3, 6.2_

  - [x] 4.2 Configure Search Agent for entity extraction
    - Create Search Agent using Agent.create() with Tavily tool
    - System prompt: Research topic, extract entities, return structured JSON
    - Include source URL and excerpt for each entity
    - Let Mentalist decide when/how to use agent (no WorkflowTask)
    - _Requirements: 4.1, 4.2_

  - [x] 4.3 Configure Inspector to review output
    - Inspector is built-in (use_inspector=True)
    - Set inspector_targets=["output"] to review final output
    - Inspector provides feedback in intermediate_steps
    - Response Generator uses feedback to create final output
    - Note: Inspector reviews quality, doesn't create JSON-LD
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 4.4 Implement result receiving and JSON-LD formatting
    - Check team.run() response for completion
    - Access response.data for final output from Response Generator
    - Parse entities from response
    - API formats entities to JSON-LD Sachstand structure
    - Validate JSON-LD format using pydantic model
    - Write to ./output/sachstand_{team_id}.jsonld
    - Update team status to "completed"
    - _Requirements: 6.1, 6.4_

- [x] 5. Improve entity extraction reliability
  - [x] 5.1 Debug and fix Search Agent entity extraction
    - Current issue: Agent returns empty entities or error messages
    - Investigate Tavily tool configuration and access
    - Test agent prompts to ensure proper entity extraction
    - Verify tool authentication and permissions
    - _Requirements: 4.1, 4.2_

  - [x] 5.2 Enhance entity extraction prompts
    - Refine Search Agent system prompt for better entity extraction
    - Add explicit examples of expected JSON output format
    - Ensure agent understands to use Tavily Search tool
    - Test with various topics to validate extraction
    - _Requirements: 4.1, 4.2_

  - [x] 5.3 Add error handling for agent failures
    - Handle cases where agent returns errors or empty results
    - Log detailed error information for debugging
    - Return meaningful error messages to API clients
    - Implement fallback strategies for failed extractions
    - _Requirements: 1.1, 4.2_

- [x] 6. Create minimal monitoring UI
  - [x] 6.1 Set up React/Vue.js project
    - Initialize UI project with Vite (port 5173)
    - Configure API client for backend
    - Set up routing (dashboard, team detail)
    - _Requirements: 2.1_

  - [x] 6.2 Implement dashboard view
    - Display list of agent teams
    - Show team_id, topic, status, created_at
    - Add "Create Team" button
    - _Requirements: 2.1_

  - [x] 6.3 Implement create team form
    - Input fields for topic and goals (textarea)
    - Submit button to POST /api/v1/agent-teams
    - Display success/error messages
    - Redirect to team detail on success
    - _Requirements: 2.1_

  - [x] 6.4 Implement team detail view
    - Display team metadata (topic, goals, status)
    - Show execution log
    - Display extracted entities
    - Show JSON-LD Sachstand (formatted)
    - _Requirements: 2.3, 2.5_

- [x] 7. Write end-to-end test for walking skeleton
  - [x] 7.1 Create test with complex topic
    - Topic: "Lagebericht zur Kinderarmut in Baden-Württemberg"
    - Goals: Identify NGOs, press organizations, think tanks
    - Test infrastructure completed successfully
    - _Requirements: 9.1, 9.2_

  - [x] 7.2 Run test and verify functionality
    - Spawn agent team via API
    - Wait for completion (with timeout)
    - Verify JSON-LD file created
    - Infrastructure test passed - full UI → Backend → Agent flow works
    - _Requirements: 9.2, 9.4_

  - [x] 7.3 Document walking skeleton results
    - Infrastructure fully functional and tested end-to-end
    - UI ↔ Backend communication works
    - Backend ↔ Agent execution works
    - Documented in E2E_TEST_SUCCESS.md
    - _Requirements: 9.5_

- [x] 8. Get working entity extraction with JSON output
  - [x] 8.1 Simplify Search Agent prompt for reliable JSON output
    - Remove complex instructions, focus on simple JSON structure
    - Request plain JSON (not markdown, not Python dict string)
    - Test with simple topic first (e.g., "Paris France")
    - Verify agent returns parseable JSON with entities
    - _Requirements: 4.1, 4.2_

  - [x] 8.2 Improve EntityProcessor to handle agent output
    - Parse JSON from agent response robustly
    - Handle both JSON-LD format and simple JSON
    - Accept any valid JSON with entity information
    - Log what we receive for debugging
    - _Requirements: 4.2, 6.1_

  - [x] 8.3 Test end-to-end with real topics
    - Test: "Jugendschutz Baden-Württemberg 2025"
    - Verify we get entities back with sources
    - Verify JSON-LD Sachstand is generated
    - Document what works
    - _Requirements: 9.1, 9.2, 9.4_

## Phase 2: UI Enhancements for Testing and Debugging

- [x] 12. Implement real-time monitoring and debugging UI
  - [x] 12.1 Add auto-refresh polling to team detail page
    - Create useAutoRefresh hook that polls every 3-5 seconds when team is "pending" or "running"
    - Automatically fetch updated team data including logs and status
    - Stop polling when status changes to "completed" or "failed"
    - Add "Last updated: X seconds ago" indicator
    - Add manual refresh button for user control
    - _Requirements: 2.2_

  - [x] 12.2 Enhance execution log display with real-time updates
    - Display log entries in chronological order with timestamps
    - Auto-scroll to latest entry when new logs arrive
    - Add color coding by log level (info=blue, warning=yellow, error=red)
    - Add filter dropdown to show logs from specific agents (All, Mentalist, Search Agent, etc.)
    - Show agent name/type for each log entry
    - Make log container scrollable with fixed height
    - _Requirements: 2.2, 2.3_

  - [x] 12.3 Add comprehensive agent execution tracing viewer
    - Create new API endpoint GET /api/v1/agent-teams/{team_id}/trace
    - Extract full trace from agent_response.data.intermediate_steps
    - Display each agent step in expandable accordion sections
    - For each step show:
      - Agent name and type (Mentalist, Orchestrator, Search Agent, Inspector, etc.)
      - Input provided to the agent
      - Output generated by the agent
      - Thought/reasoning (if available)
      - Task assignment (for team agents)
      - Tool steps used (tool name, input, output)
      - Run time for that step
      - Used credits for that step
      - API calls made
    - Add copy button to copy step details
    - Color-code by agent type for easy scanning
    - Show execution flow visually (step 1 → step 2 → step 3)
    - _Requirements: 2.3_

  - [x] 12.4 Add agent configuration and execution stats viewer
    - Create new API endpoint GET /api/v1/agent-teams/{team_id}/execution-stats
    - Extract execution_stats from agent_response
    - Display overall execution statistics:
      - Total runtime (seconds)
      - Total credits consumed
      - Total API calls made
      - Session ID
      - Environment (prod/dev)
      - Timestamp
    - Show breakdown by agent/asset:
      - Runtime breakdown per agent
      - Credit breakdown per agent
      - API call breakdown per agent
    - Display agent configuration details:
      - Model used (e.g., GPT-4o Mini, GPT-4o)
      - Tools available (Tavily Search, Wikipedia, etc.)
      - System prompt/instructions for each agent
    - Show plan from Mentalist (if available):
      - Task breakdown
      - Worker assignments
      - Expected outcomes
    - Add charts/visualizations for resource usage
    - _Requirements: 2.2, 2.3_

  - [x] 12.5 Add progress indicators and status visualization
    - Show spinner/loading animation when team is "pending" or "running"
    - Display status badge with color coding (pending=gray, running=blue, completed=green, failed=red)
    - Add progress bar if interaction count is available (current/limit)
    - Show "Team is running..." message with animated dots
    - Display created/updated timestamps in human-readable format
    - _Requirements: 2.2_

- [x] 13. Fix dashboard to show all historical runs
  - [x] 13.1 Update dashboard to display all teams by default
    - Ensure GET /api/v1/agent-teams returns all teams (not just running)
    - Sort teams by created_at descending (newest first)
    - Display status badge for each team
    - Show entity count if available
    - Add filter dropdown to filter by status (All, Running, Completed, Failed)
    - _Requirements: 2.1_

  - [x] 13.2 Add team statistics to dashboard
    - Show total teams count
    - Show count by status (X running, Y completed, Z failed)
    - Add "Recent Activity" section showing last 5 teams
    - Display average completion time for completed teams
    - _Requirements: 2.1_

- [x] 14. Improve entity display in UI
  - [x] 14.1 Create entity card components
    - Design card layout for Person and Organization entities
    - Display entity type icon (👤 for Person, 🏢 for Organization)
    - Show entity name, description, and properties (jobTitle, url)
    - Display source links as clickable citations with excerpts
    - Group entities by type (Person, Organization) in separate sections
    - Add expand/collapse for entity details and sources
    - Show entity count per type
    - _Requirements: 2.3, 2.5_

  - [x] 14.2 Add entity filtering and search
    - Implement filter dropdown for entity type (All, Person, Organization)
    - Add search input to filter entities by name (case-insensitive)
    - Highlight search matches in entity cards
    - Show count of filtered entities vs total
    - Add "Clear filters" button
    - Preserve filter state when auto-refreshing
    - _Requirements: 2.3_

  - [x] 14.3 Improve JSON-LD Sachstand display
    - Add syntax highlighting for JSON-LD using library (e.g., react-json-view or prism.js)
    - Implement collapsible sections for large Sachstand
    - Add copy-to-clipboard button with success feedback
    - Add download button to save as .jsonld file
    - Show validation status (valid/invalid JSON-LD) with icon
    - Display completion status prominently (complete/partial/failed)
    - Add link to view raw JSON in new tab
    - _Requirements: 2.5, 6.4_

  - [x] 14.4 Handle empty states and errors gracefully
    - Show helpful message when no entities extracted yet
    - Display clear error messages when team fails
    - Show "No Sachstand available yet" when team is still running
    - Add retry button for failed teams
    - Provide troubleshooting tips for common issues
    - _Requirements: 2.2, 2.3_

## Phase 3: Enhanced Research Capabilities

- [x] 9. Improve entity extraction reliability for complex topics
  - [x] 9.1 Analyze entity extraction failures
    - Review test results for "Jugendschutz Baden-Württemberg 2025" and similar topics
    - Identify patterns in successful vs failed extractions
    - Document common failure modes (too specific, non-English, limited sources)
    - _Requirements: 4.1, 4.2, 9.1_

  - [x] 9.2 Refine Search Agent prompts for better extraction
    - Add examples of successful entity extraction patterns
    - Improve instructions for handling German/non-English topics
    - Add guidance for extracting entities from government sources
    - Test with previously failed topics
    - _Requirements: 4.1, 4.2_

  - [x] 9.3 Add fallback strategies for low-information topics
    - Implement multi-pass search strategy (broader then narrower)
    - Add logic to try alternative search terms
    - Provide helpful feedback when no entities found
    - _Requirements: 3.1, 4.2_

- [x] 10. Add Wikipedia tool for entity enrichment
  - [x] 10.1 Configure Wikipedia tool in team
    - Get Wikipedia tool ID from aixplain
    - Add Wikipedia tool to Search Agent or create dedicated Wikipedia Agent
    - Update agent instructions to use Wikipedia for entity verification
    - _Requirements: 8.1, 8.2_

  - [x] 10.2 Implement Wikipedia entity linking
    - Extract Wikipedia URLs for identified entities
    - Retrieve Wikidata IDs when available
    - Add sameAs property to entities with Wikipedia links
    - Store Wikipedia data in entity citations
    - _Requirements: 8.3, 8.4_

  - [x] 10.3 Test Wikipedia integration end-to-end
    - Test with entities known to be in Wikipedia (e.g., "Dr. Manfred Lucha")
    - Verify Wikipedia links appear in JSON-LD output
    - Validate Wikidata IDs are captured correctly
    - Test with multi-language Wikipedia articles
    - _Requirements: 8.1, 8.2, 9.2_

## Phase 6: MECE Decomposition and Advanced Strategy (OPTIONAL - Future Enhancement)

- [-] 26. Implement MECE decomposition in Mentalist (OPTIONAL)
  - [x] 26.1 Add MECE analysis logic to Mentalist instructions
    - Update Mentalist prompt in team_config.py to analyze topic complexity
    - Add instructions for creating MECE dimensions (people, subjects, time, geography)
    - Implement depth-first strategy for node exploration
    - Store MECE graph in shared memory (requires aixplain shared memory API)
    - _Requirements: 5.1, 7.1, 7.2_

  - [x] 26.2 Implement MECE graph tracking
    - Create data structure for MECE graph in persistent_storage.py
    - Track coverage status for each MECE node
    - Update graph as agents complete research on nodes
    - Include MECE graph in JSON-LD Sachstand output
    - Add API endpoint GET /api/v1/agent-teams/{team_id}/mece-graph
    - _Requirements: 7.3, 7.4, 7.5_

  - [x] 26.3 Test MECE decomposition with complex topics
    - Create test file tests/test_mece_decomposition.py
    - Test with broad topic requiring decomposition (e.g., "Integration policies Baden-Württemberg")
    - Verify MECE dimensions are created correctly
    - Validate depth-first exploration works
    - Check that MECE graph is included in output
    - _Requirements: 5.1, 7.1, 9.2_



- [x] 19. Enhance execution stats display and monitoring
  - [x] 19.1 Add execution stats overview to dashboard
    - Display aggregate stats across all teams (total runtime, credits, API calls)
    - Show cost trends over time with charts
    - Add filtering by date range and status
    - Display top resource-consuming teams
    - _Requirements: 2.1, 2.2_

  - [x] 19.2 Improve stats display in team detail with visualizations
    - Add pie charts for credit/runtime breakdown by agent
    - Add timeline visualization showing agent execution sequence
    - Display cost per entity metric
    - Add export functionality for stats (CSV, JSON)
    - _Requirements: 2.3_

  - [x] 19.3 Add real-time cost monitoring alerts
    - Implement cost threshold warnings in UI
    - Add notification when team exceeds expected cost
    - Display running cost estimate during execution
    - Add budget tracking per team
    - _Requirements: 2.2_

  - [x] 19.4 Export execution stats for analysis
    - Add API endpoint to export stats in CSV format
    - Include all execution metrics (runtime, credits, API calls, entity count)
    - Add batch export for multiple teams
    - Create analysis dashboard with aggregated metrics
    - _Requirements: 2.1, 2.3_

- [x] 20. Improve entity extraction quality and reliability
  - [x] 20.1 Analyze and document extraction patterns
    - Review execution logs from completed teams to identify patterns
    - Document which types of topics work well vs poorly
    - Create docs/ENTITY_EXTRACTION_PATTERNS.md with findings
    - Identify common failure modes and their causes
    - _Requirements: 9.1, 9.2_

  - [x] 20.2 Refine agent prompts based on real-world results
    - Update Search Agent prompt in api/instructions/search_agent.py based on analysis
    - Add more specific examples of successful extractions
    - Improve instructions for handling edge cases (German topics, regional topics)
    - Test refined prompts with previously failed topics
    - _Requirements: 4.1, 4.2, 9.2_

  - [x] 20.3 Add entity validation and quality checks
    - Create api/entity_validator.py module
    - Implement validation rules (e.g., reject placeholder URLs, require descriptions)
    - Add quality scoring for entities (based on source authority, completeness)
    - Filter out low-quality entities before JSON-LD generation
    - Add validation metrics to execution stats
    - _Requirements: 4.2, 6.1, 9.2_

  - [x] 20.4 Implement entity deduplication
    - Add deduplication logic to EntityProcessor.validate_and_convert_entities()
    - Merge entities with same name and type
    - Combine sources from duplicate entities
    - Use Wikipedia/Wikidata IDs for authoritative deduplication
    - Add deduplication stats to execution log
    - _Requirements: 3.3, 8.3, 8.4_

- [x] 21. Add Google Search tool as backup (OPTIONAL)
  - [x] 21.1 Configure Google Search tool
    - Get Google Search tool ID from aixplain marketplace
    - Add Google Search tool ID to Config.TOOL_IDS in api/config.py
    - Update TeamConfig.get_tools() to include Google Search
    - Update Search Agent instructions to use Google as fallback when Tavily yields <3 entities
    - _Requirements: 3.1, 3.2_

  - [x] 21.2 Test Google Search integration
    - Create tests/test_google_search_integration.py
    - Test with topics that failed with Tavily only (e.g., very specific German topics)
    - Verify Google Search provides additional entities
    - Compare results between Tavily-only and Tavily+Google configurations
    - Document when Google Search provides better results
    - _Requirements: 3.2, 9.2_

- [ ] 22. Enhance UI with better error handling and guidance
  - [ ] 22.1 Add topic validation and suggestions
    - Create ui/src/utils/topicValidator.js with validation rules
    - Validate topic before submission (min 3 words, max 100 chars, no special chars)
    - Show inline suggestions for improving topic quality
    - Add examples of good vs bad topics in CreateTeamModal
    - Display warning for overly specific topics (with year, very long)
    - _Requirements: 2.1, 9.1_

  - [ ] 22.2 Improve error messages and troubleshooting
    - Update ui/src/components/EntitiesDisplay.jsx with context-specific error messages
    - Add troubleshooting tips based on error type (no entities, API error, timeout)
    - Create docs/TROUBLESHOOTING_UI.md with common issues and solutions
    - Add "Learn More" links to relevant docs in error messages
    - Display helpful suggestions when 0 entities found (try broader topic, check spelling)
    - _Requirements: 2.2, 2.3_

  - [ ] 22.3 Add entity quality indicators
    - Show quality score badge for each entity in ui/src/components/EntityCard.jsx
    - Add special badge for Wikipedia-linked entities (✓ Wikipedia)
    - Highlight authoritative sources (government, official sites) with icon
    - Add tooltips explaining quality metrics (source authority, completeness)
    - Color-code entities by quality (high=green, medium=yellow, low=gray)
    - _Requirements: 2.3, 2.5_

- [ ] 23. Performance optimization and caching
  - [ ] 23.1 Add execution time and cost tracking
    - Create api/performance_tracker.py module
    - Track execution time per agent and per tool call
    - Calculate cost per entity metric
    - Store performance metrics in database
    - Add API endpoint GET /api/v1/performance/summary for aggregate stats
    - _Requirements: 2.2, 9.2_

  - [ ] 23.2 Implement caching for repeated topics
    - Create api/cache.py module with Redis or in-memory cache
    - Cache Sachstand results by topic hash
    - Set cache TTL (e.g., 24 hours for fresh data)
    - Add cache hit/miss metrics to execution stats
    - Add API endpoint to clear cache for specific topics
    - _Requirements: 1.1, 9.2_

  - [ ] 23.3 Optimize agent configuration for cost
    - Analyze cost breakdown by agent and tool
    - Identify opportunities to use cheaper models (GPT-4o Mini vs GPT-4o)
    - Implement dynamic model selection based on task complexity
    - Add configuration option to prefer cost optimization over speed
    - Document cost optimization strategies in docs/COST_OPTIMIZATION.md
    - _Requirements: 9.2_

## Phase 5: Firecrawl Integration (OPTIONAL - Future Enhancement)

- [ ] 24. Add Firecrawl for deep website crawling
  - [ ] 24.1 Configure Firecrawl tool
    - Get Firecrawl tool ID from aixplain marketplace (already documented: 686432a41223092cb4294d63)
    - Add Firecrawl tool ID to Config.TOOL_IDS in api/config.py
    - Create Crawl Agent using AgentFactory with Firecrawl tool
    - Add Crawl Agent to team in TeamConfig.create_team()
    - Update Mentalist instructions to use Crawl Agent for deep content extraction
    - _Requirements: 3.1, 3.2_

  - [ ] 24.2 Implement Crawl Agent instructions
    - Create api/instructions/crawl_agent.py with Firecrawl-specific instructions
    - Define when to use FIRECRAWL_MAP_URLS vs FIRECRAWL_CRAWL_URLS
    - Add logic to handle crawl job status polling
    - Implement crawl result processing and content extraction
    - Add error handling for failed crawls
    - _Requirements: 3.2_

  - [ ] 24.3 Test Firecrawl integration
    - Create tests/test_firecrawl_integration.py
    - Test URL mapping for government websites
    - Test deep crawling with content extraction
    - Verify crawled content is passed to Extraction Agent
    - Compare entity extraction with vs without Firecrawl
    - _Requirements: 3.2, 9.2_

## Phase 6: MECE Decomposition Enhancement (OPTIONAL - Future Enhancement)

- [ ] 25. Enhance MECE decomposition in Mentalist
  - [ ] 25.1 Improve MECE analysis logic
    - Update api/instructions/mentalist.py with enhanced MECE decomposition rules
    - Add heuristics for when to apply MECE (topic complexity, word count, goals)
    - Implement automatic dimension detection (people, subjects, time, geography)
    - Add depth-first node prioritization logic
    - Test with complex topics requiring decomposition
    - _Requirements: 5.1, 7.1, 7.2_

  - [ ] 25.2 Add MECE graph visualization in UI
    - Create ui/src/components/MECEGraphVisualization.jsx
    - Use D3.js or similar library for graph rendering
    - Display nodes with status (complete, in-progress, not-started)
    - Show entity count per node
    - Add interactive node selection to filter entities
    - _Requirements: 2.4, 7.3_

  - [ ] 25.3 Implement MECE-aware entity aggregation
    - Update EntityProcessor to group entities by MECE node
    - Add MECE node metadata to each entity in JSON-LD
    - Calculate coverage percentage per dimension
    - Identify gaps in MECE coverage
    - Add MECE coverage report to Sachstand
    - _Requirements: 7.3, 7.4, 7.5_

## Phase 7: Evaluation Suite and Production Deployment (OPTIONAL - Future Enhancement)

- [ ] 27. Create comprehensive evaluation suite
  - [ ] 27.1 Define evaluation metrics and test cases
    - Create tests/evaluation/test_cases.json with representative topics
    - Define metrics: entity count, source quality, Wikipedia coverage, cost, runtime
    - Create ground truth datasets for known topics
    - Document evaluation methodology in docs/EVALUATION.md
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ] 27.2 Implement automated evaluation framework
    - Create tests/evaluation/run_evaluation.py script
    - Run all test cases and collect metrics
    - Compare results against ground truth
    - Generate evaluation report with charts
    - Add CI/CD integration for regression testing
    - _Requirements: 9.2, 9.4_

  - [ ] 27.3 Benchmark against baseline
    - Run evaluation suite with current configuration
    - Document baseline metrics (entity count, accuracy, cost)
    - Identify areas for improvement
    - Create improvement roadmap based on findings
    - _Requirements: 9.2, 9.5_

- [ ] 28. Production deployment preparation
  - [ ] 28.1 Add production configuration
    - Create production environment configuration
    - Switch to GPT-4o for production (better quality)
    - Add rate limiting and request throttling
    - Implement API authentication and authorization
    - Add monitoring and alerting (Sentry, DataDog)
    - _Requirements: 1.1_

  - [ ] 28.2 Create deployment documentation
    - Document deployment process in docs/DEPLOYMENT.md
    - Create Docker containers for API and UI
    - Write docker-compose.yml for local deployment
    - Document environment variables and configuration
    - Create deployment checklist
    - _Requirements: 1.1_

  - [ ] 28.3 Set up production monitoring
    - Implement health checks and readiness probes
    - Add application metrics (request count, latency, errors)
    - Set up log aggregation (ELK stack or CloudWatch)
    - Create dashboards for monitoring
    - Configure alerts for critical errors
    - _Requirements: 2.2_
