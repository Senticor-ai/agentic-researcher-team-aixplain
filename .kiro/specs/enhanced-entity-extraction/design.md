# Design Document: Enhanced Entity Extraction

## Overview

This design enhances the OSINT agent team system to extract a comprehensive set of entity types beyond just Person and Organization. The system will extract Topics, Events, and Policies, with special emphasis on temporal information (dates, deadlines, effective dates). Additionally, the system will leverage Wikipedia for entity discovery, validation, and relationship exploration to surface additional relevant entities.

The enhancement maintains the existing architecture principle: **API invokes, monitors, stores - agents do the extraction work**. All entity extraction logic remains in the agent instructions, not in the API layer.

## Key Design Principles

### 1. Exhaustive Research Over Quick Completion

The system prioritizes thorough research over speed:
- **Use full interaction limit**: Agents should use all 50 steps, not return early
- **Multi-round searches**: Multiple search rounds with different terms and strategies
- **Feedback loops**: After each round, assess coverage and identify gaps
- **Iterative refinement**: Each round builds on previous findings

### 2. Diverse Search Strategies

To ensure comprehensive coverage:
- **Round 1**: Direct topic search
- **Round 2**: Alternative terms and underrepresented entity types
- **Round 3**: Deep dive into specific entities and authoritative sources
- **Round 4**: Wikipedia discovery and relationship exploration

### 3. Coverage-Based Completion

Stop only when:
- Interaction limit nearly exhausted (< 5 steps remaining)
- AND comprehensive coverage achieved (≥10 entities, all types represented)
- AND recent searches yielding only duplicates

## Architecture

### High-Level Changes

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  • Entity processing (UNCHANGED)                             │
│  • JSON-LD generation (ENHANCED for new types)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   aixplain Team Agent                        │
│                                                              │
│  User-Defined Agents (ENHANCED):                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Search Agent (ENHANCED)                          │    │
│  │   - Extracts: Person, Organization, Topic,         │    │
│  │     Event, Policy                                  │    │
│  │   - Includes temporal information for Events       │    │
│  │   - Extracts from ALL search results               │    │
│  │                                                     │    │
│  │ • Wikipedia Agent (ENHANCED)                       │    │
│  │   - Validates extracted entities                   │    │
│  │   - Discovers related entities (especially Topics  │    │
│  │     and Events)                                    │    │
│  │   - Follows Wikipedia links for entity discovery   │    │
│  │   - Extracts temporal information from Wikipedia   │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Component Changes

1. **Search Agent Instructions** (ENHANCED)
   - Add Topic, Event, Policy entity extraction
   - Emphasize extracting from ALL search results
   - Include temporal information extraction
   - Add examples for new entity types

2. **Wikipedia Agent Instructions** (ENHANCED)
   - Add entity discovery from Wikipedia pages
   - Extract related Topics and Events
   - Follow Wikipedia links to discover more entities
   - Extract temporal information from Wikipedia

3. **Data Models** (NEW)
   - TopicEntity model
   - EventEntity model
   - PolicyEntity model

4. **Entity Processor** (ENHANCED)
   - Handle new entity types in parsing
   - Support temporal fields in entities

5. **Entity Validator** (ENHANCED)
   - Validate new entity types
   - Quality scoring for new types

## Components and Interfaces

### 1. Data Models (api/models.py)

#### New Entity Models

```python
class TopicEntity(BaseModel):
    """Schema.org Topic/Thing entity"""
    type: Literal["Topic"] = Field(default="Topic")
    name: str = Field(..., description="Topic name")
    description: Optional[str] = Field(None, description="Topic description")
    about: Optional[str] = Field(None, description="What this topic is about")
    sources: List[EntitySource] = Field(default_factory=list)
    sameAs: Optional[List[str]] = Field(None, description="Wikipedia/Wikidata URLs")
    wikidata_id: Optional[str] = Field(None)
    wikipedia_links: Optional[List[dict]] = Field(None)
    quality_score: Optional[float] = Field(None)

class EventEntity(BaseModel):
    """Schema.org Event entity"""
    type: Literal["Event"] = Field(default="Event")
    name: str = Field(..., description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    startDate: Optional[str] = Field(None, description="Event start date (ISO 8601)")
    endDate: Optional[str] = Field(None, description="Event end date (ISO 8601)")
    location: Optional[str] = Field(None, description="Event location")
    organizer: Optional[str] = Field(None, description="Event organizer")
    sources: List[EntitySource] = Field(default_factory=list)
    sameAs: Optional[List[str]] = Field(None)
    wikidata_id: Optional[str] = Field(None)
    wikipedia_links: Optional[List[dict]] = Field(None)
    quality_score: Optional[float] = Field(None)

class PolicyEntity(BaseModel):
    """Schema.org Legislation/Policy entity"""
    type: Literal["Policy"] = Field(default="Policy")
    name: str = Field(..., description="Policy/legislation name")
    description: Optional[str] = Field(None, description="Policy description")
    legislationIdentifier: Optional[str] = Field(None, description="Official identifier")
    dateCreated: Optional[str] = Field(None, description="Enactment date (ISO 8601)")
    dateModified: Optional[str] = Field(None, description="Last modified date (ISO 8601)")
    legislationDate: Optional[str] = Field(None, description="Effective date (ISO 8601)")
    expirationDate: Optional[str] = Field(None, description="Expiration date (ISO 8601)")
    legislationJurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    sources: List[EntitySource] = Field(default_factory=list)
    sameAs: Optional[List[str]] = Field(None)
    wikidata_id: Optional[str] = Field(None)
    wikipedia_links: Optional[List[dict]] = Field(None)
    quality_score: Optional[float] = Field(None)
```

### 2. Search Agent Instructions (api/instructions/search_agent.py)

#### Enhanced Instructions

**Key Changes:**
- Add entity type definitions for Topic, Event, Policy
- Provide examples for each new entity type
- Emphasize extracting from ALL search results
- Include temporal information extraction guidelines
- Add minimum entity extraction requirement per search result
- Support iterative searches with different strategies
- Provide feedback on search effectiveness

**Output Format Enhancement:**

```
TOPIC: [Topic Name]
Description: [2-3 sentences about the topic]
Sources:
- [URL]: "[Excerpt from source]"

EVENT: [Event Name]
Date: [ISO 8601 date or date range]
Location: [Location if available]
Description: [2-3 sentences about the event]
Sources:
- [URL]: "[Excerpt from source]"

POLICY: [Policy Name]
Identifier: [Official ID if available]
Effective Date: [ISO 8601 date]
Jurisdiction: [Jurisdiction]
Description: [2-3 sentences about the policy]
Sources:
- [URL]: "[Excerpt from source]"
```

**Extraction Strategy:**
1. Process each search result systematically
2. Extract at minimum the source organization from each result
3. Look for Topics mentioned in titles and content
4. Look for Events with dates (announcements, deadlines, effective dates)
5. Look for Policies with identifiers and dates
6. Extract temporal information in ISO 8601 format when possible

### 3. Mentalist Agent Instructions (api/instructions/mentalist.py)

#### Enhanced Instructions for Iterative Research

**Key Changes:**
- Emphasize exhaustive research using full interaction limit
- Implement multi-round search strategy with different terms
- Add feedback loops to assess coverage and identify gaps
- Continue searching until interaction limit reached or comprehensive coverage achieved
- Use alternative search terms and strategies in subsequent rounds

**Iterative Research Strategy:**

```python
def get_mentalist_instructions(topic, goals, topic_analysis, alternatives, has_wikipedia_agent):
    return f"""You are the strategic research coordinator for an OSINT team.

CRITICAL: EXHAUSTIVE RESEARCH REQUIRED
- You have {interaction_limit} interaction steps available
- USE ALL AVAILABLE STEPS for thorough research
- Do NOT return early - continue until interaction limit is nearly exhausted
- Each search round should use different terms and strategies
- Aim for comprehensive coverage, not quick completion

MULTI-ROUND SEARCH STRATEGY:

Round 1: Direct Search (Steps 1-15)
- Search for the main topic directly
- Extract initial entities
- Assess what entity types are found

Round 2: Alternative Terms (Steps 16-30)
- Use alternative search terms: {alternatives}
- Search for specific entity types that were underrepresented
- If few Topics found, search: "[topic] themes", "[topic] issues"
- If few Events found, search: "[topic] events", "[topic] timeline", "[topic] deadlines"
- If few Policies found, search: "[topic] regulations", "[topic] laws", "[topic] guidelines"

Round 3: Deep Dive (Steps 31-45)
- Search for specific entities found in Round 1 and 2
- Search for related organizations and people
- Search for government sources: "[topic] site:.gov", "[topic] site:.de"
- Use Google Search if Tavily yielded limited results

Round 4: Wikipedia Discovery (Steps 46-50)
- Send all extracted entities to Wikipedia Agent
- Wikipedia Agent discovers related entities
- Assess final coverage and gaps

FEEDBACK LOOPS:
After each round, assess:
- How many entities of each type have been extracted?
- Which entity types are underrepresented?
- What search terms should be tried next?
- Are we finding new information or seeing duplicates?
- Have we exhausted this search strategy?

CONTINUE SEARCHING IF:
- Total entities < 10
- Any entity type has 0 entities
- Topics < 3 or Events < 2
- Still finding new entities in recent searches
- Interaction steps remaining > 5

ONLY STOP WHEN:
- Interaction limit nearly exhausted (< 5 steps remaining)
- AND comprehensive coverage achieved (≥10 entities, all types represented)
- AND recent searches yielding only duplicates

SEARCH TERM VARIATIONS:
Use these patterns for thorough coverage:
- "[topic]" - direct search
- "[topic] overview" - broad context
- "[topic] key players" - people and organizations
- "[topic] timeline" - events
- "[topic] regulations" - policies
- "[topic] themes" - topics
- "[topic] site:.gov" - authoritative sources
- "[topic] site:.de" - German sources
- "[entity name] [topic]" - entity-specific searches

Remember: Research quality is measured by thoroughness, not speed.
Use your full interaction budget to provide comprehensive results.
"""
```

### 4. Wikipedia Agent Instructions (api/instructions/wikipedia_agent.py)

#### Enhanced Instructions

**Key Changes:**
- Add entity discovery from Wikipedia pages
- Extract related entities (especially Topics and Events)
- Follow Wikipedia links to discover more entities
- Extract temporal information from Wikipedia infoboxes
- Prioritize Topics and Events in discovery

**Discovery Strategy:**

```python
def get_wikipedia_agent_instructions() -> str:
    return """You are a Wikipedia linking and discovery agent.

YOUR TASKS:
1. Validate entities by searching Wikipedia
2. Discover related entities from Wikipedia pages
3. Extract Topics and Events mentioned on Wikipedia pages
4. Follow Wikipedia links to discover additional relevant entities
5. Extract temporal information (dates, deadlines)

ENTITY DISCOVERY:
- When you find a Wikipedia page for an entity, scan it for:
  * Related topics in the "See also" section
  * Events mentioned with dates
  * Related people and organizations
  * Policies and regulations mentioned
- Follow links to related topics (up to 2 levels deep)
- Extract entities from infoboxes (dates, locations, relationships)

TOPIC DISCOVERY:
- Look for category tags on Wikipedia pages
- Extract main topics from the article introduction
- Follow "See also" links for related topics
- Extract topics from section headings

EVENT DISCOVERY:
- Look for dates in infoboxes
- Extract events from "History" or "Timeline" sections
- Look for scheduled events or deadlines
- Extract effective dates for policies/regulations

OUTPUT FORMAT:
{{
  "validated_entities": [...],  // Original entities with Wikipedia links
  "discovered_entities": [      // NEW entities found via Wikipedia
    {{
      "entity_type": "Topic",
      "name": "...",
      "description": "...",
      "source": "https://en.wikipedia.org/wiki/...",
      "discovered_via": "Related to [original entity name]"
    }},
    {{
      "entity_type": "Event",
      "name": "...",
      "description": "...",
      "startDate": "2024-01-15",
      "source": "https://en.wikipedia.org/wiki/...",
      "discovered_via": "Mentioned on [original entity name] page"
    }}
  ]
}}
"""
```

### 4. Entity Processor (api/entity_processor.py)

#### Enhanced Parsing

**Changes to `parse_text_format` method:**

```python
@staticmethod
def parse_text_format(text: str) -> Dict[str, Any]:
    """
    Parse structured text format from Search Agent
    
    ENHANCED to support: PERSON, ORGANIZATION, TOPIC, EVENT, POLICY
    """
    entities = []
    
    # Split by entity type markers
    sections = re.split(
        r'\n(?=\*{0,2}(?:PERSON|ORGANIZATION|TOPIC|EVENT|POLICY):)', 
        text
    )
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Determine entity type
        if section.startswith('TOPIC:') or section.startswith('**TOPIC:'):
            entity = parse_topic_entity(section)
        elif section.startswith('EVENT:') or section.startswith('**EVENT:'):
            entity = parse_event_entity(section)
        elif section.startswith('POLICY:') or section.startswith('**POLICY:'):
            entity = parse_policy_entity(section)
        elif section.startswith('PERSON:') or section.startswith('**PERSON:'):
            entity = parse_person_entity(section)  # Existing
        elif section.startswith('ORGANIZATION:') or section.startswith('**ORGANIZATION:'):
            entity = parse_organization_entity(section)  # Existing
        else:
            continue
        
        if entity:
            entities.append(entity)
    
    return {"entities": entities}
```

**New Helper Methods:**

```python
@staticmethod
def parse_topic_entity(section: str) -> Optional[Dict[str, Any]]:
    """Parse TOPIC entity from text section"""
    name_match = re.match(r'\*{0,2}TOPIC:\s*(.+?)(\*{0,2})?\n', section)
    if not name_match:
        return None
    
    name = name_match.group(1).strip().strip('*')
    description = extract_field(section, 'Description')
    sources = extract_sources(section)
    
    return {
        "type": "Topic",
        "name": name,
        "description": description or "",
        "sources": sources
    }

@staticmethod
def parse_event_entity(section: str) -> Optional[Dict[str, Any]]:
    """Parse EVENT entity from text section"""
    name_match = re.match(r'\*{0,2}EVENT:\s*(.+?)(\*{0,2})?\n', section)
    if not name_match:
        return None
    
    name = name_match.group(1).strip().strip('*')
    description = extract_field(section, 'Description')
    date = extract_field(section, 'Date')
    location = extract_field(section, 'Location')
    sources = extract_sources(section)
    
    entity = {
        "type": "Event",
        "name": name,
        "description": description or "",
        "sources": sources
    }
    
    if date:
        entity["startDate"] = date
    if location:
        entity["location"] = location
    
    return entity

@staticmethod
def parse_policy_entity(section: str) -> Optional[Dict[str, Any]]:
    """Parse POLICY entity from text section"""
    name_match = re.match(r'\*{0,2}POLICY:\s*(.+?)(\*{0,2})?\n', section)
    if not name_match:
        return None
    
    name = name_match.group(1).strip().strip('*')
    description = extract_field(section, 'Description')
    identifier = extract_field(section, 'Identifier')
    effective_date = extract_field(section, 'Effective Date')
    jurisdiction = extract_field(section, 'Jurisdiction')
    sources = extract_sources(section)
    
    entity = {
        "type": "Policy",
        "name": name,
        "description": description or "",
        "sources": sources
    }
    
    if identifier:
        entity["legislationIdentifier"] = identifier
    if effective_date:
        entity["legislationDate"] = effective_date
    if jurisdiction:
        entity["legislationJurisdiction"] = jurisdiction
    
    return entity
```

**Changes to `receive_entities_from_agent` method:**
- Handle discovered_entities from Wikipedia Agent
- Merge discovered entities with validated entities
- Log statistics about entity types extracted

### 5. Entity Validator (api/entity_validator.py)

#### Enhanced Validation

**Changes to `validate_entity` method:**

```python
@staticmethod
def validate_entity(entity: Dict[str, Any]) -> Tuple[bool, List[str], float]:
    """
    Validate an entity and return validation result
    
    ENHANCED to support: Topic, Event, Policy
    """
    issues = []
    entity_type = entity.get("type")
    
    # Check required fields
    if not entity.get("name"):
        issues.append("Missing required field: name")
    
    if not entity_type:
        issues.append("Missing required field: type")
    elif entity_type not in ["Person", "Organization", "Topic", "Event", "Policy"]:
        issues.append(f"Invalid entity type: {entity_type}")
    
    # Type-specific validation
    if entity_type == "Event":
        # Events should have dates when possible
        if not entity.get("startDate"):
            issues.append("Event missing startDate (recommended)")
    
    if entity_type == "Policy":
        # Policies should have dates or identifiers
        if not entity.get("legislationDate") and not entity.get("legislationIdentifier"):
            issues.append("Policy missing both legislationDate and legislationIdentifier (at least one recommended)")
    
    # Calculate quality score
    quality_score = EntityValidator.calculate_quality_score(entity)
    
    # Determine validity
    is_valid = len(issues) == 0 or quality_score >= EntityValidator.MIN_QUALITY_SCORE
    
    return is_valid, issues, quality_score
```

**Changes to `calculate_quality_score` method:**

```python
@staticmethod
def calculate_quality_score(entity: Dict[str, Any]) -> float:
    """
    Calculate quality score for an entity (0.0 to 1.0)
    
    ENHANCED scoring for new entity types
    """
    score = 0.0
    entity_type = entity.get("type")
    
    # Base scoring (same for all types)
    if entity.get("name") and len(entity.get("name", "")) >= 2:
        score += 0.2
    
    if entity.get("description") and len(entity.get("description", "")) >= 10:
        score += 0.2
    
    # Source validation
    sources = entity.get("sources", [])
    if sources:
        valid_sources = [s for s in sources if EntityValidator.is_valid_url(s.get("url", ""))]
        if valid_sources:
            score += 0.2
            if any(EntityValidator.is_authoritative_source(s.get("url", "")) for s in valid_sources):
                score += 0.2
    
    # Type-specific scoring
    if entity_type == "Event":
        if entity.get("startDate"):
            score += 0.1
        if entity.get("location"):
            score += 0.05
    
    if entity_type == "Policy":
        if entity.get("legislationDate"):
            score += 0.1
        if entity.get("legislationIdentifier"):
            score += 0.05
    
    # Wikipedia enrichment
    if entity.get("sameAs") or entity.get("wikidata_id"):
        score += 0.1
    
    return min(score, 1.0)
```

### 6. Wikipedia Entity Discovery

#### New Method in EntityProcessor

```python
@staticmethod
def merge_discovered_entities(
    original_entities: List[Dict[str, Any]], 
    discovered_entities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge discovered entities from Wikipedia with original entities
    
    Args:
        original_entities: Entities from Search Agent
        discovered_entities: Entities discovered via Wikipedia
        
    Returns:
        Combined list with duplicates removed
    """
    all_entities = original_entities.copy()
    
    for discovered in discovered_entities:
        # Check if entity already exists
        is_duplicate = False
        for existing in all_entities:
            if (existing.get("name", "").lower() == discovered.get("name", "").lower() and
                existing.get("type") == discovered.get("type")):
                is_duplicate = True
                # Merge sources
                existing_sources = existing.get("sources", [])
                discovered_sources = discovered.get("sources", [])
                existing["sources"] = existing_sources + discovered_sources
                break
        
        if not is_duplicate:
            all_entities.append(discovered)
            logger.info(f"Added discovered entity: {discovered.get('name')} ({discovered.get('type')})")
    
    return all_entities
```

## Data Models

### Schema.org Mapping

| Entity Type | Schema.org Type | Key Properties |
|-------------|----------------|----------------|
| Person | schema:Person | name, jobTitle, description, sources |
| Organization | schema:Organization | name, url, description, sources |
| Topic | schema:Thing | name, about, description, sources |
| Event | schema:Event | name, startDate, endDate, location, organizer, sources |
| Policy | schema:Legislation | name, legislationIdentifier, legislationDate, legislationJurisdiction, sources |

### Temporal Information Format

All dates should be in ISO 8601 format:
- Date: `2024-01-15`
- Date with time: `2024-01-15T10:00:00Z`
- Date range: Use `startDate` and `endDate` fields

## Error Handling

### Entity Type Validation
- If unknown entity type encountered, log warning and skip
- Continue processing other entities
- Include error in feedback message

### Temporal Information Parsing
- If date format is invalid, log warning but keep entity
- Store original date string in description if parsing fails
- Mark entity with lower quality score if temporal info missing

### Wikipedia Discovery Failures
- If Wikipedia Agent fails, continue with original entities
- Log warning about Wikipedia enrichment failure
- Don't block main extraction pipeline

## Testing Strategy

### Unit Tests
1. Test new entity model validation
2. Test enhanced text format parsing for Topic, Event, Policy
3. Test quality scoring for new entity types
4. Test entity deduplication with new types
5. Test temporal information extraction

### Integration Tests
1. Test Search Agent with new entity types
2. Test Wikipedia Agent entity discovery
3. Test end-to-end extraction with all entity types
4. Test discovered entities merging with original entities

### Test Data
- Create sample search results with Topics, Events, Policies
- Create sample Wikipedia pages with related entities
- Test with German and English content
- Test with various date formats

## Performance Considerations

### Wikipedia Discovery
- Limit depth of Wikipedia link following (max 2 levels)
- Limit number of discovered entities per original entity (max 5)
- Cache Wikipedia lookups to avoid redundant API calls
- Set timeout for Wikipedia searches (30 seconds)

### Entity Processing
- Process entities in batches if count > 50
- Log progress for long-running extractions
- Implement early termination if quality threshold not met

## Migration Strategy

### Backward Compatibility
- Existing Person and Organization extraction unchanged
- New entity types are additive
- Old data format still supported
- UI gracefully handles missing entity types

### Rollout Plan
1. Deploy enhanced Search Agent instructions
2. Deploy enhanced Wikipedia Agent instructions
3. Deploy new data models and validation
4. Update UI to display new entity types
5. Monitor extraction quality and adjust

## Monitoring and Feedback

### Research Progress Tracking

The system should log progress after each search round:

```python
{
  "round": 2,
  "steps_used": 28,
  "steps_remaining": 22,
  "entities_extracted": {
    "Person": 3,
    "Organization": 5,
    "Topic": 2,
    "Event": 1,
    "Policy": 0
  },
  "coverage_assessment": "Underrepresented: Policy, Event, Topic",
  "next_strategy": "Search for policies and events with terms: 'regulations', 'timeline', 'deadlines'"
}
```

### Feedback to Mentalist

After each Search Agent invocation, provide feedback:
- Number of new entities found (vs duplicates)
- Entity types found
- Gaps in coverage
- Suggested next search terms
- Whether to continue or try different strategy

### Early Warning Indicators

Log warnings if:
- Interaction steps < 30 and status = "completed" (returned too early)
- Total entities < 5 (insufficient coverage)
- Any entity type completely missing
- No new entities found in last 2 rounds (search exhausted)

## Success Metrics

### Research Thoroughness
- Average interaction steps used per run (target: ≥ 45 out of 50)
- Number of search rounds per run (target: ≥ 3)
- Percentage of runs using > 80% of interaction limit (target: ≥ 80%)

### Extraction Completeness
- Average entities extracted per search result (target: ≥ 1.5)
- Total entities per run (target: ≥ 10)
- Percentage of search results yielding at least one entity (target: ≥ 90%)
- Distribution of entity types (target: ≥ 20% Topics, ≥ 10% Events)

### Wikipedia Discovery
- Percentage of entities validated in Wikipedia (target: ≥ 50%)
- Average discovered entities per run (target: ≥ 3)
- Percentage of discovered entities that are Topics or Events (target: ≥ 60%)

### Quality
- Average quality score across all entity types (target: ≥ 0.6)
- Percentage of entities with temporal information when relevant (target: ≥ 70%)
- Percentage of entities with authoritative sources (target: ≥ 40%)
