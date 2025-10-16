# Design Document

## Overview

This design enhances the agent team system to ensure schema.org compliance, URL validation, and Wikipedia enrichment through an agent-first architecture. The key innovation is using a **one-piece flow** approach where Search and Wikipedia agents work on individual entities, with the Orchestrator collecting and validating results using Python-based validation tools. This ensures data quality at the source while maintaining efficient workflow coordination.

## Architecture

### Hive Mind Approach

Instead of a fixed workflow, we use a **hive mind** architecture where agents collaborate through shared memory. All agents are peers that can call each other. The Validation Agent is available to any agent that wants to validate an entity immediately - no need to wait until the end.

```
                    Shared Memory (Entity Pool)
                            ↕
        ┌───────────────────┼───────────────────┬───────────────────┐
        ↓                   ↓                   ↓                   ↓
   Search Agent      Ontology Agent      Wikipedia Agent    Validation Agent
   (discovers)       (suggests)          (enriches)         (validates)
        ↓                   ↓                   ↓                   ↓
   Adds entities     Suggests types      Adds Wikipedia     Validates entities
   with sources      & relationships     & Wikidata         anytime, on-demand
        ↓                   ↓                   ↓                   ↓
        └───────────────────┴───────────────────┴───────────────────┘
                            ↕ (agents can call each other)
                            ↓
                    Orchestrator observes
                    (facilitates, doesn't control)
                            ↓
                    Response Generator
                    (synthesizes when ready)

Example flows:
- Search Agent finds entity → calls Validation Agent → validates URLs immediately
- Wikipedia Agent enriches entity → calls Validation Agent → validates schema.org
- Ontology Agent suggests type → other agents can call Validation Agent to verify
- Orchestrator can call Validation Agent anytime to check pool status
```

### Key Architectural Principles

1. **Shared Memory**: All agents read/write to shared entity pool - no rigid handoffs
2. **Peer Agents**: All agents are peers that can call each other - no hierarchy
3. **On-Demand Validation**: Any agent can call Validation Agent anytime to validate entities
4. **Immediate Feedback**: Validation happens as entities are created/modified, not at the end
5. **Autonomous Agents**: Each agent works independently, deciding what to work on
6. **Opportunistic Enrichment**: Agents enrich entities when they see opportunities
7. **Emergent Quality**: Quality emerges from agent collaboration, not enforced workflow
8. **Orchestrator as Facilitator**: Orchestrator observes and facilitates, doesn't dictate flow

## Components and Interfaces

### 1. Schema.org Validator Tool (Python)

A custom aixplain tool that validates entities against schema.org specifications.

**Tool Configuration:**
- **Type**: Python Function Tool
- **Input**: Entity JSON object
- **Output**: Validation result with issues and corrections

**Functionality:**
```python
def validate_schema_org(entity: dict) -> dict:
    """
    Validate entity against schema.org specifications
    
    Returns:
        {
            "valid": bool,
            "issues": [list of validation issues],
            "corrections": {dict of suggested corrections},
            "entity_type": str,
            "schema_url": str
        }
    """
```

**Validation Checks:**
- Entity has @context field pointing to "https://schema.org"
- Entity @type is a valid schema.org type
- All properties are valid for the entity type
- Property values match expected schema.org data types
- Required properties are present

**Integration:**
- Registered as an aixplain tool accessible to the Orchestrator
- Orchestrator calls this tool for each collected entity
- Returns structured feedback for correction

### 2. URL Verification Tool (Python)

A custom aixplain tool that verifies URLs are valid and accessible.

**Tool Configuration:**
- **Type**: Python Function Tool
- **Input**: List of URLs to verify
- **Output**: Verification results with accessibility status

**Functionality:**
```python
def verify_urls(urls: list[str]) -> dict:
    """
    Verify URLs are valid and accessible
    
    Returns:
        {
            "total_urls": int,
            "valid_urls": int,
            "invalid_urls": int,
            "results": [
                {
                    "url": str,
                    "valid": bool,
                    "accessible": bool,
                    "status_code": int,
                    "issue": str (if any)
                }
            ]
        }
    """
```

**Verification Checks:**
- URL format validation (proper protocol, domain, path)
- HTTP HEAD request to check accessibility
- Response status code validation (200-299 = success)
- Timeout handling (5 second timeout)
- Common URL corrections (add https://, fix encoding)

**Integration:**
- Registered as an aixplain tool accessible to the Orchestrator
- Orchestrator extracts all URLs from entities and calls this tool
- Returns structured feedback for URL issues

### 3. Enhanced Orchestrator Agent (Facilitator Role)

The Orchestrator facilitates collaboration but doesn't control the flow.

**Responsibilities:**
1. **Shared Memory Management**: Maintain entity pool accessible to all agents
2. **Agent Spawning**: Spawn Search and Wikipedia agents with access to shared memory
3. **Validation Monitoring**: Run validation tools periodically on entity pool
4. **Issue Broadcasting**: Broadcast validation issues to relevant agents
5. **Readiness Assessment**: Determine when entity pool is ready for Response Generator

**Hive Mind Facilitation Logic:**
```
1. Initialize shared memory (entity pool)

2. Spawn autonomous agents with shared memory access:
   - Search Agent: "Find entities and add to pool. Check pool for entities needing better sources."
   - Wikipedia Agent: "Monitor pool for entities. Enrich any entity that could benefit from Wikipedia data."

3. Continuously (every N interactions):
   - Run URL Verification Tool on entities in pool
   - Run Schema.org Validator Tool on entities in pool
   - Broadcast issues to agents:
     * "Entity 'X' has invalid URLs - Search Agent, can you find better sources?"
     * "Entity 'Y' needs Wikipedia enrichment - Wikipedia Agent, please enrich"
     * "Entity 'Z' has schema.org issues - agents, please review"

4. Agents respond autonomously:
   - Search Agent might improve sources for flagged entities
   - Search Agent might also discover new entities
   - Wikipedia Agent might enrich flagged entities
   - Wikipedia Agent might also enrich other entities it notices

5. When entity pool stabilizes (no new entities, validation issues resolved):
   - Signal Response Generator to synthesize output
   - Response Generator reads from shared memory

No rigid workflow - agents work on what they see as valuable.
```

**Shared Memory Structure:**
```python
{
    "entities": [
        {
            "id": "entity_1",
            "data": {...},
            "status": "needs_wikipedia",  # or "needs_sources", "validated", etc.
            "validation_issues": [...],
            "last_updated_by": "search_agent",
            "update_count": 2
        }
    ],
    "validation_metrics": {...}
}
```

### 4. Enhanced Search Agent (Autonomous Discoverer)

The Search Agent works autonomously, discovering entities and improving sources based on validation feedback.

**Autonomous Behavior:**
1. **Entity Discovery**: Search for entities related to research topic
2. **Pool Awareness**: Check shared memory to avoid duplicates
3. **Source Quality**: Prioritize authoritative sources (.gov, .de, official sites)
4. **Self-Improvement**: Monitor pool for entities with invalid sources and improve them
5. **Schema.org Format**: Add entities in schema.org format from the start

**Agent Instructions:**
```
You are the Search Agent. You have access to shared memory containing entities and can call other agents.

Your role:
- Search for entities related to the research topic
- Add discovered entities to the shared memory pool
- Use schema.org format: include @context and @type fields
- Prioritize authoritative sources (.gov, .de, official domains)
- AFTER adding an entity, call Validation Agent to validate URLs immediately
- If Validation Agent reports issues, improve the entity before moving on
- Monitor the pool for entities with status "needs_sources" or "invalid_urls"
- If you see an entity with poor sources, improve it by finding better sources
- Check for duplicates before adding new entities

You work autonomously - discover entities, validate them immediately, and improve existing ones when you see opportunities. Don't wait until the end to validate - validate as you go!
```

### 5. Ontology Agent (Semantic Improvement Suggester)

The Ontology Agent suggests improvements to entity types and relationships, helping the hive mind produce semantically rich data.

**Autonomous Behavior:**
1. **Type Suggestions**: Suggest more specific or appropriate schema.org types
2. **Relationship Discovery**: Identify potential relationships between entities
3. **Schema.org Expertise**: Deep knowledge of schema.org type hierarchy and properties
4. **Improvement Opportunities**: Find entities that could benefit from semantic enrichment
5. **Gentle Guidance**: Suggest rather than enforce - let other agents decide

**Agent Instructions:**
```
You are the Ontology Agent with deep expertise in schema.org ontologies. You have access to shared memory containing entities.

Your role is to suggest improvements, not enforce them:

- Monitor the entity pool for entities that could benefit from ontology improvements
- Suggest more specific schema.org types when appropriate:
  * "Entity 'Bundesministerium' could use @type 'GovernmentOrganization' instead of 'Organization' for better semantic clarity"
  * "Entity 'Climate Summit 2024' could be 'ConferenceEvent' instead of just 'Event'"
- Suggest relationships between entities:
  * "Person 'Angela Merkel' could have 'worksFor' relationship with 'Bundesregierung'"
  * "Event 'Climate Summit' could have 'organizer' property linking to 'UN'"
- Suggest additional schema.org properties that would add semantic value:
  * "Organization could benefit from 'parentOrganization' property"
  * "Person could include 'alumniOf' for educational background"
- Find opportunities for semantic consistency across related entities

You work autonomously - look for improvement opportunities and suggest them to the hive mind. Other agents (especially Search and Wikipedia agents) can choose to act on your suggestions. Your expertise helps the hive mind discover semantic richness they might have missed.

Be encouraging and helpful, not prescriptive. Sometimes entities are fine as-is!
```

**Example Improvements:**
```json
// Before
{
    "@type": "Organization",
    "name": "Bundesministerium für Umwelt"
}

// After (Ontology Agent improvement)
{
    "@type": "GovernmentOrganization",
    "name": "Bundesministerium für Umwelt",
    "alternateName": "BMU",
    "parentOrganization": {
        "@type": "GovernmentOrganization",
        "name": "Bundesregierung Deutschland"
    }
}
```

### 6. Validation Agent (Quality Checker)

The Validation Agent uses validation tools to continuously check entity quality and broadcast issues to the hive mind.

**Autonomous Behavior:**
1. **Continuous Validation**: Periodically validate entities in the pool
2. **Tool Usage**: Use Schema.org Validator and URL Verifier tools
3. **Issue Broadcasting**: Broadcast validation issues to relevant agents
4. **Quality Metrics**: Track validation metrics for Inspector
5. **Readiness Assessment**: Help determine when entity pool is ready

**Agent Instructions:**
```
You are the Validation Agent. You have access to shared memory and validation tools:
- Schema.org Validator tool: Validates entities against schema.org specifications
- URL Verifier tool: Verifies URLs are valid and accessible

Your role is to validate entities on-demand and proactively:

ON-DEMAND (when other agents call you):
- When Search Agent calls you: Validate URLs using URL Verifier tool
- When Wikipedia Agent calls you: Validate schema.org compliance using Schema.org Validator tool
- When Ontology Agent calls you: Validate suggested types and relationships
- When Orchestrator calls you: Validate entire entity pool and provide metrics
- Return immediate feedback: "Valid" or specific issues found

PROACTIVE (autonomous monitoring):
- Periodically scan the entity pool for entities that haven't been validated recently
- Validate them and update their status
- If you find issues, broadcast to the hive mind:
  * "Entity 'X' has invalid URLs - Search Agent, can you find better sources?"
  * "Entity 'Y' is missing @context field - needs schema.org review"
  * "Entity 'Z' could benefit from Wikipedia enrichment"

Update entity status based on validation:
- "validated" - passed all checks
- "needs_sources" - has invalid URLs
- "needs_schema_review" - schema.org issues
- "needs_wikipedia" - missing Wikipedia data

Track validation metrics for reporting. You're available anytime any agent needs validation - respond quickly and helpfully!
```

**Tool Integration:**
```python
# Validation Agent uses tools
validation_agent = AgentFactory.create(
    name="Validation Agent",
    role="Quality Checker",
    tools=[
        schema_validator_tool,  # Python tool for schema.org validation
        url_verifier_tool       # Python tool for URL verification
    ],
    instructions=validation_agent_instructions
)
```

### 7. Enhanced Wikipedia Agent (Autonomous Enricher)

The Wikipedia Agent works autonomously, monitoring the entity pool and enriching entities opportunistically.

**Autonomous Behavior:**
1. **Pool Monitoring**: Continuously check shared memory for entities
2. **Opportunity Detection**: Identify entities that could benefit from Wikipedia data
3. **Proactive Enrichment**: Enrich entities even if not explicitly requested
4. **Schema.org Compliance**: Ensure all enrichments follow schema.org format
5. **Self-Validation**: Verify Wikipedia URLs before adding them

**Agent Instructions:**
```
You are the Wikipedia Agent. You have access to shared memory containing entities and can call other agents.

Your role:
- Monitor the entity pool for entities that could benefit from Wikipedia enrichment
- Look for entities with status "needs_wikipedia" or entities without Wikipedia data
- Proactively enrich entities with:
  * sameAs property (Wikipedia and Wikidata URLs)
  * wikidata_id property
  * wikipedia_links array (multilingual)
- Ensure all additions follow schema.org format
- AFTER enriching an entity, call Validation Agent to validate schema.org compliance
- If Validation Agent reports issues, fix them before moving on
- Update entity status to "enriched" when validated
- If you can't find Wikipedia data, mark status as "no_wikipedia_available"

You work autonomously - don't wait for instructions. If you see an entity that needs enrichment, enrich it and validate immediately.
```

**Output Format:**
```json
{
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Angela Merkel",
    "description": "German politician...",
    "sameAs": [
        "https://en.wikipedia.org/wiki/Angela_Merkel",
        "https://www.wikidata.org/wiki/Q567"
    ],
    "wikidata_id": "Q567",
    "wikipedia_links": [
        {"language": "en", "url": "https://en.wikipedia.org/wiki/Angela_Merkel"},
        {"language": "de", "url": "https://de.wikipedia.org/wiki/Angela_Merkel"}
    ]
}
```

### 8. Enhanced Response Generator

The Response Generator creates final output with schema.org compliance built-in.

**Enhancements:**
1. **Schema.org Template**: Use schema.org compliant templates for all entity types
2. **Validation Feedback Integration**: Apply corrections from validation tools
3. **URL Correction**: Fix malformed URLs based on verification feedback
4. **Deduplication**: Merge duplicate entities using Wikidata IDs as authoritative identifiers
5. **Quality Metrics**: Include validation metrics in output

**Output Structure:**
```json
{
    "@context": "https://schema.org",
    "@type": "ResearchReport",
    "name": "Research on [Topic]",
    "dateCreated": "2025-10-16T...",
    "about": {
        "@type": "Topic",
        "name": "[Topic]"
    },
    "hasPart": [
        // Array of validated, schema.org compliant entities
    ],
    "validationMetrics": {
        "totalEntities": 25,
        "validEntities": 24,
        "schemaOrgCompliance": 0.96,
        "urlValidationRate": 0.98,
        "wikipediaEnrichmentRate": 0.85
    }
}
```

### 9. Enhanced Inspector Agent

The Inspector reviews validation metrics and provides final quality assessment.

**Enhancements:**
1. **Validation Metrics Review**: Analyze metrics from validation tools
2. **Quality Thresholds**: Check if metrics meet minimum quality standards
3. **Issue Reporting**: Report any entities that failed validation
4. **Recommendation**: Provide recommendations for improving data quality

**Quality Thresholds:**
- Schema.org compliance: >= 95%
- URL validation rate: >= 90%
- Wikipedia enrichment rate: >= 70% (for entities that have Wikipedia pages)

## Data Models

### Entity with Schema.org Compliance

```python
class SchemaOrgEntity(BaseModel):
    """Base schema.org entity with validation"""
    context: str = Field("https://schema.org", alias="@context")
    type: str = Field(..., alias="@type")
    name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None  # Validated URL
    sameAs: Optional[List[HttpUrl]] = None  # Wikipedia, Wikidata URLs
    wikidata_id: Optional[str] = None
    wikipedia_links: Optional[List[Dict[str, str]]] = None
    sources: List[EntitySource] = Field(default_factory=list)
    
    # Validation metadata
    validation_status: Optional[str] = None  # "valid", "corrected", "failed"
    validation_issues: Optional[List[str]] = None
    quality_score: Optional[float] = None
```

### Validation Result

```python
class ValidationResult(BaseModel):
    """Result from validation tools"""
    entity_name: str
    entity_type: str
    schema_org_valid: bool
    schema_org_issues: List[str] = Field(default_factory=list)
    url_validation: Dict[str, Any]
    corrections_applied: List[str] = Field(default_factory=list)
    quality_score: float
    passed: bool
```

### Validation Metrics

```python
class ValidationMetrics(BaseModel):
    """Aggregated validation metrics"""
    total_entities: int
    valid_entities: int
    corrected_entities: int
    failed_entities: int
    
    schema_org_compliance_rate: float
    url_validation_rate: float
    wikipedia_enrichment_rate: float
    
    avg_quality_score: float
    
    issues_by_type: Dict[str, int]
    corrections_by_type: Dict[str, int]
```

## Error Handling

### Validation Failures

1. **Schema.org Validation Failure**:
   - Log detailed validation issues
   - Attempt automatic correction (add @context, fix type casing)
   - If correction fails, flag entity for manual review
   - Include entity in output with validation_status="failed"

2. **URL Verification Failure**:
   - Log inaccessible URLs
   - Attempt common corrections (add protocol, fix encoding)
   - If >30% of entity URLs fail, flag entity as low-quality
   - Continue processing but mark URLs as unverified

3. **Wikipedia Enrichment Failure**:
   - Log entities without Wikipedia data
   - Continue processing without Wikipedia links
   - Do not fail entity validation due to missing Wikipedia data

### Tool Execution Errors

1. **Validation Tool Timeout**:
   - Set 10 second timeout for validation tools
   - If timeout occurs, log error and skip validation for that entity
   - Mark entity as "validation_skipped"

2. **Tool Execution Error**:
   - Catch and log tool execution errors
   - Continue workflow without validation
   - Report tool errors to Inspector

### Correction Cycles

1. **Maximum Correction Attempts**: 2 cycles
2. **Correction Tracking**: Track which entities have been corrected
3. **Infinite Loop Prevention**: If entity fails validation after 2 corrections, accept as-is with warnings

## Testing Strategy

### Unit Tests

1. **Schema.org Validator Tool**:
   - Test validation of valid entities
   - Test detection of invalid @context
   - Test detection of invalid @type
   - Test detection of invalid properties
   - Test correction suggestions

2. **URL Verification Tool**:
   - Test validation of valid URLs
   - Test detection of malformed URLs
   - Test accessibility checking
   - Test timeout handling
   - Test URL correction logic

3. **Entity Models**:
   - Test Pydantic validation
   - Test HttpUrl validation
   - Test schema.org field aliases

### Integration Tests

1. **One-Piece Flow**:
   - Test Search Agent → Wikipedia Agent flow for single entity
   - Test Orchestrator collection of multiple entities
   - Test validation tool integration

2. **Validation Workflow**:
   - Test end-to-end validation workflow
   - Test correction feedback loop
   - Test quality gating

3. **Wikipedia Enrichment**:
   - Test Wikipedia Agent schema.org output
   - Test sameAs property population
   - Test multilingual link handling

### End-to-End Tests

1. **Full Team Execution**:
   - Test complete research workflow with validation
   - Verify all entities are schema.org compliant
   - Verify all URLs are validated
   - Verify Wikipedia enrichment works

2. **Quality Metrics**:
   - Verify validation metrics are calculated correctly
   - Verify metrics are included in output
   - Verify Inspector receives metrics

3. **Error Scenarios**:
   - Test handling of invalid entities
   - Test handling of inaccessible URLs
   - Test handling of missing Wikipedia data

## Implementation Notes

### Python Tool Creation

Python validation tools will be created using the aixplain SDK:

```python
from aixplain.factories import ToolFactory

# Create schema.org validator tool
schema_validator = ToolFactory.create(
    name="Schema.org Validator",
    description="Validates entities against schema.org specifications",
    function=validate_schema_org,
    parameters={
        "entity": {
            "type": "object",
            "description": "Entity to validate"
        }
    }
)

# Create URL verification tool
url_verifier = ToolFactory.create(
    name="URL Verifier",
    description="Verifies URLs are valid and accessible",
    function=verify_urls,
    parameters={
        "urls": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of URLs to verify"
        }
    }
)
```

### Orchestrator Configuration

The Orchestrator will be configured as a facilitator with access to validation tools:

```python
orchestrator = AgentFactory.create(
    name="Orchestrator",
    role="Hive Mind Facilitator",
    tools=[
        schema_validator,  # Validation tool
        url_verifier       # Validation tool
    ],
    instructions="""
    You are the Orchestrator facilitating a hive mind of research agents.

    Your role is to facilitate, not control:
    
    1. Maintain shared memory (entity pool) accessible to all agents
    
    2. Spawn autonomous peer agents with shared memory access:
       - Search Agent: "Find entities, add to pool, call Validation Agent to validate URLs immediately. Work autonomously."
       - Ontology Agent: "Suggest schema.org type improvements and relationships. Work autonomously."
       - Wikipedia Agent: "Enrich entities with Wikipedia data, call Validation Agent to validate schema.org. Work autonomously."
       - Validation Agent: "Available on-demand for any agent. Also proactively scan pool and broadcast issues. Work autonomously."
    
    3. Observe the hive mind collaboration:
       - Agents call Validation Agent as they work (immediate validation)
       - Validation Agent also proactively scans and broadcasts issues
       - Search Agent discovers entities and validates URLs immediately
       - Ontology Agent suggests improvements
       - Wikipedia Agent enriches and validates schema.org immediately
       - Agents respond to each other's work and validation feedback autonomously
    
    4. Monitor hive mind progress:
       - Are agents finding and enriching entities?
       - Is Validation Agent reporting fewer issues over time?
       - Is the entity pool stabilizing (fewer updates)?
    
    5. When ready (entity pool stable, most entities validated):
       - Signal Response Generator to synthesize output from shared memory
    
    Trust the agents. They're autonomous and will collaborate through shared memory. Your job is to facilitate and know when they're done.
    
    Sometimes the Search Agent will bring back amazing entities with perfect sources - celebrate that! Sometimes Ontology Agent will add rich semantic relationships - let it happen! Sometimes Wikipedia Agent will enrich entities beautifully - encourage it! The hive mind works best when agents are free to contribute their strengths.
    
    The Validation Agent will keep everyone honest by continuously checking quality and broadcasting issues. Other agents will respond autonomously to improve the entity pool.
    """
)
```

### Response Generator Updates

The Response Generator instructions will be updated to ensure schema.org compliance:

```python
response_generator_instructions = """
Create final JSON-LD output with schema.org compliance:

1. Use @context: "https://schema.org" for all entities
2. Use proper @type values (Person, Organization, Event, etc.)
3. Include sameAs property with Wikipedia/Wikidata URLs
4. Include wikidata_id property
5. Include wikipedia_links array with multilingual links
6. Ensure all URLs are properly formatted
7. Apply any corrections from validation feedback
8. Include validation metrics in output

Output format:
{
    "@context": "https://schema.org",
    "@type": "ResearchReport",
    "hasPart": [validated entities],
    "validationMetrics": {metrics}
}
"""
```

## Performance Considerations

### One-Piece Flow Benefits

1. **Faster Feedback**: Issues detected immediately per entity
2. **Better Quality**: Each entity validated before moving to next
3. **Easier Debugging**: Clear entity-level tracing
4. **Reduced Memory**: Don't need to hold all entities in memory

### Validation Tool Performance

1. **Caching**: Cache schema.org type definitions to avoid repeated lookups
2. **Batch URL Verification**: Verify multiple URLs in parallel
3. **Timeout Management**: Set reasonable timeouts to prevent blocking
4. **Async Execution**: Use async HTTP requests for URL verification

### Scalability

1. **Entity Limit**: Validate up to 100 entities per execution
2. **URL Limit**: Verify up to 500 URLs per execution
3. **Timeout**: Overall validation timeout of 60 seconds
4. **Fallback**: If validation times out, continue without validation

## Migration Path

### Phase 1: Create Validation Tools
1. Implement schema.org validator Python function
2. Implement URL verifier Python function
3. Register tools with aixplain
4. Test tools independently

### Phase 2: Update Orchestrator
1. Update Orchestrator instructions for validation workflow
2. Add validation tools to Orchestrator configuration
3. Implement entity collection logic
4. Test Orchestrator with validation tools

### Phase 3: Update Wikipedia Agent
1. Update Wikipedia Agent instructions for schema.org output
2. Add sameAs, wikidata_id, wikipedia_links properties
3. Test Wikipedia Agent output format

### Phase 4: Update Response Generator
1. Update Response Generator instructions for schema.org compliance
2. Add validation metrics to output
3. Implement correction feedback handling
4. Test Response Generator with validated entities

### Phase 5: Update Inspector
1. Update Inspector to review validation metrics
2. Add quality threshold checks
3. Add validation reporting
4. Test Inspector with validation data

### Phase 6: Integration Testing
1. Test complete workflow end-to-end
2. Verify schema.org compliance
3. Verify URL validation
4. Verify Wikipedia enrichment
5. Verify validation metrics

### Phase 7: Deployment
1. Deploy updated team configuration
2. Monitor validation metrics
3. Adjust quality thresholds based on results
4. Document validation process
