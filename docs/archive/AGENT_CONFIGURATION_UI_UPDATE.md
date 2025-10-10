# Agent Configuration UI Update

## Overview

Updated the agent configuration display to provide **equal, detailed information for all agents** - both built-in and user-defined. Each agent now gets the same amount of space and detail in the UI.

## Changes Made

### Backend (`api/main.py`)

#### Built-in Agents - Enhanced Details

Each built-in agent now includes:
- **Name** and **Role**
- **Detailed description** (2-3 sentences explaining what they do)
- **Model** information (GPT-4o or GPT-4o Mini)
- **Capabilities** list (5 specific capabilities per agent)

**Example - Mentalist:**
```json
{
  "name": "Mentalist",
  "role": "Strategic Planner",
  "description": "Analyzes the research topic and creates a dynamic research strategy using MECE decomposition for complex topics. Plans on-the-fly without following a fixed workflow, adapting to the specific needs of each research request.",
  "model": "GPT-4o Mini",
  "capabilities": [
    "Topic analysis and complexity assessment",
    "MECE (Mutually Exclusive, Collectively Exhaustive) decomposition",
    "Dynamic research strategy planning",
    "Agent task coordination",
    "Adaptive workflow generation"
  ]
}
```

#### User-Defined Agents - Enhanced Details

Each user-defined agent now includes:
- **Name** and **Role**
- **Detailed description** (2-3 sentences)
- **Model** information
- **Tools** list with IDs
- **Capabilities** list (6 specific capabilities)
- **Additional metadata** (search strategy, languages supported)

**Example - Search Agent:**
```json
{
  "name": "Search Agent",
  "role": "OSINT Research Specialist",
  "tools": ["Tavily Search", "Google Search (backup)"],
  "tool_ids": ["6736411cf127849667606689", "65c51c556eb563350f6e1bb1"],
  "description": "Performs comprehensive web searches to find information and extract entities (Person, Organization). Uses Tavily Search as primary tool and automatically falls back to Google Search when Tavily yields fewer than 3 entities, ensuring comprehensive coverage especially for German government topics and official sources.",
  "model": "GPT-4o Mini",
  "capabilities": [
    "Web search using Tavily (AI-optimized) and Google Search (comprehensive)",
    "Person and Organization entity extraction",
    "Real source URLs and excerpts citation",
    "German and English language search support",
    "Automatic fallback strategy for better coverage",
    "Government and official source prioritization"
  ],
  "search_strategy": "Primary: Tavily → Fallback: Google Search (if <3 entities)"
}
```

**Example - Wikipedia Agent:**
```json
{
  "name": "Wikipedia Agent",
  "role": "Entity Enrichment Specialist",
  "tools": ["Wikipedia"],
  "tool_ids": ["6633fd59821ee31dd914e232"],
  "description": "Enriches extracted entities with authoritative Wikipedia links and Wikidata IDs for entity linking and deduplication. Searches Wikipedia in multiple languages (German, English, French) to find the most relevant articles and adds sameAs properties for cross-referencing.",
  "model": "GPT-4o Mini",
  "capabilities": [
    "Wikipedia entity verification and lookup",
    "Multi-language Wikipedia URL retrieval (de, en, fr)",
    "Wikidata ID extraction for authoritative linking",
    "sameAs property generation for deduplication",
    "Entity cross-referencing and validation",
    "Authoritative source attribution"
  ],
  "languages_supported": ["de", "en", "fr"]
}
```

### Frontend (`ui/src/components/TeamConfigInfo.jsx`)

#### Enhanced Agent Card Display

**Built-in Agents now show:**
- Agent icon and name
- Role (with color coding)
- Full description
- Model tag
- Capabilities list (5 items)

**User-Defined Agents now show:**
- Agent icon and name
- Role (with color coding)
- Tool tags (e.g., "Tavily Search", "Google Search (backup)")
- Full description
- Model tag
- Search strategy (for Search Agent)
- Languages supported (for Wikipedia Agent)
- Capabilities list (6 items)

### CSS (`ui/src/components/TeamConfigInfo.css`)

Added styles for:
- `.agent-model` - Model tag display
- `.agent-strategy` - Search strategy display with background
- `.agent-languages` - Languages supported display with background

## Visual Result

### Before
- Built-in agents: Name, role, 1-line description
- User-defined agents: Name, tools, 1-line description, capabilities

### After
- **All agents get equal treatment:**
  - Name and role
  - 2-3 sentence detailed description
  - Model information
  - 5-6 capabilities listed
  - Additional metadata (strategy, languages)

## Benefits

1. **Equal Representation**: Every agent gets the same level of detail
2. **Better Understanding**: Users can see exactly what each agent does
3. **Model Transparency**: Shows which model powers each agent
4. **Tool Clarity**: Clear indication of which tools are available
5. **Strategy Visibility**: Search strategy is explicitly shown
6. **Language Support**: Multi-language capabilities are highlighted

## Example UI Display

```
Built-in Micro Agents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Mentalist
   Strategic Planner
   
   Analyzes the research topic and creates a dynamic research strategy using 
   MECE decomposition for complex topics. Plans on-the-fly without following 
   a fixed workflow, adapting to the specific needs of each research request.
   
   [GPT-4o Mini]
   
   Capabilities:
   • Topic analysis and complexity assessment
   • MECE (Mutually Exclusive, Collectively Exhaustive) decomposition
   • Dynamic research strategy planning
   • Agent task coordination
   • Adaptive workflow generation

[Similar detailed cards for Inspector, Orchestrator, Feedback Combiner, Response Generator]

User-Defined Agents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔎 Search Agent
   OSINT Research Specialist
   [Tavily Search] [Google Search (backup)]
   
   Performs comprehensive web searches to find information and extract entities 
   (Person, Organization). Uses Tavily Search as primary tool and automatically 
   falls back to Google Search when Tavily yields fewer than 3 entities, ensuring 
   comprehensive coverage especially for German government topics and official sources.
   
   [GPT-4o Mini]
   
   Search Strategy: Primary: Tavily → Fallback: Google Search (if <3 entities)
   
   Capabilities:
   • Web search using Tavily (AI-optimized) and Google Search (comprehensive)
   • Person and Organization entity extraction
   • Real source URLs and excerpts citation
   • German and English language search support
   • Automatic fallback strategy for better coverage
   • Government and official source prioritization

📚 Wikipedia Agent
   Entity Enrichment Specialist
   [Wikipedia]
   
   Enriches extracted entities with authoritative Wikipedia links and Wikidata IDs 
   for entity linking and deduplication. Searches Wikipedia in multiple languages 
   (German, English, French) to find the most relevant articles and adds sameAs 
   properties for cross-referencing.
   
   [GPT-4o Mini]
   
   Languages: de, en, fr
   
   Capabilities:
   • Wikipedia entity verification and lookup
   • Multi-language Wikipedia URL retrieval (de, en, fr)
   • Wikidata ID extraction for authoritative linking
   • sameAs property generation for deduplication
   • Entity cross-referencing and validation
   • Authoritative source attribution
```

## Testing

1. **Restart backend:**
   ```bash
   poetry run python -m api.main
   ```

2. **Restart frontend:**
   ```bash
   cd ui && npm run dev
   ```

3. **Visit:** http://localhost:5174/

4. **Click "Show Details"** on the Agent Team Configuration card

5. **Verify:**
   - All built-in agents show 5 capabilities
   - All user-defined agents show 6 capabilities
   - Search Agent shows both Tavily and Google Search tools
   - Search Agent shows search strategy
   - Wikipedia Agent shows languages supported
   - All agents show model information

## Files Modified

1. `api/main.py` - Enhanced `get_agent_configuration()` function
2. `ui/src/components/TeamConfigInfo.jsx` - Updated agent card rendering
3. `ui/src/components/TeamConfigInfo.css` - Added styles for new elements
4. `docs/AGENT_CONFIGURATION_UI_UPDATE.md` - This documentation

## Conclusion

All agents now receive equal, detailed representation in the UI, making it clear what each agent does, which tools they use, and how they contribute to the research process. The Google Search integration is prominently displayed as a backup tool for the Search Agent.
