# UI Updates for Wikipedia Integration

## Changes Made

The UI has been updated to display the Wikipedia Agent alongside the Search Agent in the team configuration.

### Files Modified

#### 1. `ui/src/components/TeamConfigInfo.jsx`

**Added Wikipedia Agent to User-Defined Agents:**
```javascript
{
  name: "Wikipedia Agent",
  description: "Entity enrichment agent with Wikipedia tool",
  tools: ["Wikipedia API"],
  capabilities: [
    "Search Wikipedia for entity verification",
    "Retrieve Wikipedia URLs in multiple languages (de, en, fr)",
    "Extract Wikidata IDs for entity linking",
    "Add sameAs properties for deduplication"
  ],
  icon: "📚",
  color: "#e67e22"
}
```

**Updated Summary Display:**
- Changed from "1 Agent (Tavily Search)" to "2 Agents (Search + Wikipedia)"

**Added Wikipedia Agent to Coordination Roles:**
```javascript
{
  agent: "Wikipedia Agent",
  responsibility: "Enriches extracted entities with Wikipedia links and Wikidata IDs",
  note: "Called after entity extraction to add authoritative references"
}
```

#### 2. `ui/src/pages/TeamDetail.jsx`

**Added Wikipedia Agent Color:**
```javascript
const getAgentTypeColor = (agentType) => {
  const colors = {
    'mentalist': '#9b59b6',
    'orchestrator': '#3498db',
    'inspector': '#e74c3c',
    'search': '#2ecc71',
    'wikipedia': '#e67e22',  // NEW: Wikipedia agent color
    'response': '#f39c12',
    'unknown': '#95a5a6'
  };
  return colors[agentType?.toLowerCase()] || colors.unknown;
};
```

This ensures that when Wikipedia Agent appears in the execution trace, it will be displayed with the orange color (#e67e22).

## UI Display

### Team Configuration Info

When users expand the "Agent Team Configuration" section, they will now see:

**User-Defined Agents:**
1. **Search Agent** 🔎 (Green)
   - Tavily Search API
   - Web search and entity extraction
   
2. **Wikipedia Agent** 📚 (Orange)
   - Wikipedia API
   - Entity enrichment with Wikipedia links and Wikidata IDs

### Agent Execution Trace

When the Wikipedia Agent executes, it will appear in the trace with:
- **Color**: Orange (#e67e22)
- **Name**: Wikipedia Agent
- **Steps**: Showing Wikipedia search and enrichment operations

### Coordination Flow

The coordination section now shows:
1. Mentalist → Plans strategy
2. Orchestrator → Routes to Search Agent
3. Search Agent → Extracts entities
4. **Wikipedia Agent → Enriches entities** (NEW)
5. Inspector → Reviews quality
6. Response Generator → Creates output

## Dynamic Display

The UI is designed to dynamically display agents based on the actual execution:

- **TeamConfigInfo**: Shows the pre-configured agents (Search + Wikipedia)
- **TeamDetail Trace**: Dynamically displays agents from the actual execution trace
- **Agent Colors**: Automatically applied based on agent type

## Testing the UI

1. **Start the UI**:
   ```bash
   cd ui
   npm run dev
   ```

2. **Navigate to**: http://localhost:5173/

3. **View Team Configuration**:
   - Click "Show Details" on the Agent Team Configuration card
   - Verify Wikipedia Agent appears in User-Defined Agents section
   - Check that it shows 2 Agents in the summary

4. **Create a Team**:
   - Create a new research team
   - Wait for execution to complete

5. **View Execution Trace**:
   - Open the team detail page
   - Scroll to "Agent Execution Trace"
   - Look for Wikipedia Agent steps (if Mentalist invoked it)
   - Verify orange color is applied

## Expected Behavior

### When Wikipedia Agent is Invoked

If the Mentalist decides to use the Wikipedia Agent, you should see:

1. **In Execution Trace**:
   - Step showing "Wikipedia Agent" with orange badge
   - Input: List of entities to enrich
   - Output: Enriched entities with Wikipedia links

2. **In Entity Display**:
   - Entities with `sameAs` property showing Wikipedia URLs
   - Wikidata IDs displayed as identifiers

### When Wikipedia Agent is Not Invoked

If the Mentalist doesn't invoke the Wikipedia Agent:
- Only Search Agent steps will appear in trace
- Entities won't have Wikipedia enrichment
- This is normal - Mentalist decides dynamically

## Future Enhancements

Potential UI improvements for Wikipedia integration:

1. **Wikipedia Link Display**: Add Wikipedia icon/link in entity cards
2. **Wikidata Badge**: Show Wikidata ID as a badge on entities
3. **Multi-language Indicator**: Show flags for different Wikipedia language versions
4. **Wikipedia Preview**: Hover tooltip showing Wikipedia excerpt
5. **Agent Statistics**: Track Wikipedia agent usage and success rate

## Notes

- The UI updates are **backward compatible** - teams without Wikipedia agent will still work
- Agent colors are consistent across the application
- The Wikipedia agent will only appear in execution traces when actually invoked by the Mentalist
- The configuration display shows the **available** agents, not necessarily the ones used in every execution
