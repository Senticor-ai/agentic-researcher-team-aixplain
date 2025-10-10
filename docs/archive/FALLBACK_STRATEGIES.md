# Fallback Strategies for Entity Extraction

## Overview

This document describes the fallback strategies implemented to improve entity extraction reliability when initial searches yield insufficient results.

**Date**: 2025-10-09  
**Task**: 9.3 - Add fallback strategies for low-information topics  
**Files Created/Modified**:
- `api/search_strategy.py` - New module for search strategy logic
- `api/agent_config.py` - Integrated fallback strategies
- `api/team_config.py` - Integrated fallback strategies
- `api/main.py` - Added feedback generation
- `api/models.py` - Added feedback field to AgentTeamDetail

---

## Problem Statement

From the entity extraction analysis, we identified that:
- 91.7% of extractions failed (no entities found)
- German topics had ~0% success rate
- Very specific topics (with years, qualifiers) consistently failed
- Niche administrative topics had limited online sources

**Root Cause**: Single-pass search with original topic often yields no results for:
- Very specific topics (e.g., "Jugendschutz Baden-Württemberg 2025")
- Niche administrative topics (e.g., "Wertstoffsammlungen")
- Topics with limited online coverage

---

## Solution: Multi-Pass Search Strategy

### Architecture

The fallback strategy is implemented as a **search strategy module** that:
1. Analyzes the topic to understand its characteristics
2. Generates alternative search terms (broader → narrower)
3. Enhances agent instructions with multi-pass search logic
4. Provides helpful feedback when extraction fails

**Key Principle**: The agent still does the searching - we just provide better instructions and alternative terms.

### Components

#### 1. Topic Analysis

**Function**: `SearchStrategy.analyze_topic(topic: str)`

Analyzes the topic to determine:
- **Language**: Detected language (de, en, mixed)
- **Specificity**: Level of specificity (broad, medium, specific, very_specific)
- **Domain**: Topic domain (government, social, technical, general)
- **Has Year**: Whether topic includes a specific year
- **Has Location**: Whether topic includes a location

**Example**:
```python
topic = "Jugendschutz Baden-Württemberg 2025"
analysis = analyze_topic(topic)
# Returns:
# {
#   "language": "de",
#   "specificity": "very_specific",
#   "domain": "government",
#   "has_year": True,
#   "has_location": True
# }
```

#### 2. Alternative Search Terms Generation

**Function**: `SearchStrategy.generate_alternative_terms(topic: str, analysis: dict)`

Generates alternative search terms using multiple strategies:

**Strategy 1: Remove Year**
- For very specific topics with years
- Example: "Jugendschutz Baden-Württemberg 2025" → "Jugendschutz Baden-Württemberg"

**Strategy 2: Broaden by Removing Modifiers**
- Remove report-type words (Lagebericht, Sachstand, Report, etc.)
- Example: "Sozialer Lagebericht Baden-Württemberg" → "Sozialer Baden-Württemberg"

**Strategy 3: Focus on Core Concept**
- Extract main noun phrases (first 2-3 meaningful words)
- Example: "Lagebericht zur Kinderarmut in Baden-Württemberg" → "Kinderarmut Baden-Württemberg"

**Strategy 4: Add Context for Broad Topics**
- For very broad topics, add context
- Example: "Paris" → "Paris organizations", "Paris officials"

**Strategy 5: Domain-Specific Alternatives**
- For government topics: Add "Ministerium", "Behörde"
- For social topics: Add "NGO", "Verein"
- Example: "Jugendarmut Baden-Württemberg" → "Jugendarmut Baden-Württemberg NGO"

**Example Output**:
```python
topic = "Jugendschutz Baden-Württemberg 2025"
alternatives = generate_alternative_terms(topic)
# Returns:
# [
#   "Jugendschutz Baden-Württemberg",  # No year
#   "Jugendschutz Baden-Württemberg Ministerium",  # Domain-specific
#   "Jugendschutz Baden-Württemberg Behörde"  # Domain-specific
# ]
```

#### 3. Multi-Pass Instructions

**Function**: `SearchStrategy.generate_multi_pass_instructions(topic, analysis, alternatives)`

Generates instructions for the agent to perform multi-pass searches:

```
MULTI-PASS SEARCH STRATEGY:

Your initial search for "Jugendschutz Baden-Württemberg 2025" may yield limited results. 
If so, try these fallback strategies:

TOPIC ANALYSIS:
- Language: DE
- Specificity: very_specific
- Domain: government
- Has specific year: Yes
- Has location: Yes

FALLBACK SEARCH TERMS (try in order if initial search yields <3 entities):
1. "Jugendschutz Baden-Württemberg"
2. "Jugendschutz Baden-Württemberg Ministerium"
3. "Jugendschutz Baden-Württemberg Behörde"

SEARCH STRATEGY:
1. Start with the original topic
2. If you find <3 entities, try the first alternative term
3. If still <3 entities, try the next alternative term
4. Continue until you find sufficient entities or exhaust alternatives
5. Combine results from all successful searches

WHEN TO USE ALTERNATIVES:
- Initial search returns 0 entities → Try alternative 1
- Initial search returns 1-2 entities → Try alternative 1, combine results
- Initial search returns 3+ entities → No need for alternatives

IMPORTANT:
- Always try at least 2 search terms before giving up
- Combine entities from multiple searches (deduplicate by name)
- Prefer more specific entities over generic ones
- Always include real source URLs
```

#### 4. Helpful Feedback Generation

**Function**: `SearchStrategy.generate_helpful_feedback(topic, analysis, entity_count)`

Generates user-friendly feedback based on extraction results:

**When No Entities Found**:
```
No entities found for topic: Jugendschutz Baden-Württemberg 2025

Possible reasons:
- Topic is very specific (includes year or many qualifiers)
  → Try a broader search without the year or specific qualifiers
- Topic is in German, which may have limited online sources
  → Try searching for related English terms or broader German topics
- Regional topics may have limited coverage
  → Try searching without the specific location

Suggestions:
- Try searching: "Jugendschutz Baden-Württemberg"
- Try searching: "Jugendschutz Baden-Württemberg Ministerium"
- Try searching: "Jugendschutz Baden-Württemberg Behörde"
```

**When Few Entities Found**:
```
Only 2 entity(ies) found for topic: Jugendschutz Baden-Württemberg 2025

This is a low number. Consider:
- Trying broader search terms
- Searching for related organizations or officials
- Checking if the topic has sufficient online coverage
```

**When Good Results**:
```
Found 5 entities for topic: Jugendschutz Baden-Württemberg 2025
This is a good result!
```

---

## Integration

### Agent Configuration

The search strategy is integrated into agent configuration:

**In `agent_config.py`**:
```python
from api.search_strategy import enhance_instructions

# ... in get_walking_skeleton_config()
system_prompt = """..."""  # Base prompt

# Enhance with fallback strategies
system_prompt = enhance_instructions(topic, system_prompt)
```

**In `team_config.py`**:
```python
from api.search_strategy import enhance_instructions, analyze_topic, generate_alternative_terms

# ... in create_search_agent()
system_prompt = """..."""  # Base prompt
system_prompt = enhance_instructions(topic, system_prompt)

# ... in create_team()
topic_analysis = analyze_topic(topic)
alternatives = generate_alternative_terms(topic)

# Include analysis and alternatives in Mentalist instructions
mentalist_instructions = f"""
TOPIC ANALYSIS:
- Language: {topic_analysis['language'].upper()}
- Specificity: {topic_analysis['specificity']}
...

ALTERNATIVE SEARCH TERMS (if initial search yields <3 entities):
1. "{alternatives[0]}"
2. "{alternatives[1]}"
...
"""
```

### API Feedback

The API now provides helpful feedback in the response:

**In `api/main.py`**:
```python
from api.search_strategy import generate_feedback

@app.get("/api/v1/agent-teams/{team_id}")
async def get_agent_team(team_id: str):
    # ... get team data
    
    # Generate helpful feedback
    if team["status"] == "completed":
        entity_count = len(team.get("sachstand", {}).get("hasPart", []))
        feedback = generate_feedback(team["topic"], entity_count)
    
    return AgentTeamDetail(
        # ... other fields
        feedback=feedback
    )
```

**In `api/models.py`**:
```python
class AgentTeamDetail(BaseModel):
    # ... other fields
    feedback: Optional[str] = Field(None, description="Helpful feedback about extraction results")
```

---

## Usage Examples

### Example 1: Very Specific German Topic

**Topic**: "Jugendschutz Baden-Württemberg 2025"

**Analysis**:
- Language: German
- Specificity: Very specific (has year)
- Domain: Government

**Alternative Terms Generated**:
1. "Jugendschutz Baden-Württemberg" (no year)
2. "Jugendschutz Baden-Württemberg Ministerium" (add ministry)
3. "Jugendschutz Baden-Württemberg Behörde" (add agency)

**Agent Behavior**:
1. Searches "Jugendschutz Baden-Württemberg 2025" → 0 entities
2. Tries "Jugendschutz Baden-Württemberg" → 2 entities found
3. Tries "Jugendschutz Baden-Württemberg Ministerium" → 1 more entity
4. Returns combined 3 entities

### Example 2: Niche Administrative Topic

**Topic**: "Wertstoffsammlungen in Baden-Württemberg"

**Analysis**:
- Language: German
- Specificity: Specific
- Domain: Technical/Administrative

**Alternative Terms Generated**:
1. "Wertstoffsammlungen Baden-Württemberg" (simplified)
2. "Abfallwirtschaft Baden-Württemberg" (broader concept)
3. "Recycling Baden-Württemberg" (English equivalent)

**Agent Behavior**:
1. Searches original → 0 entities
2. Tries alternatives → May find waste management organizations
3. If still 0, provides helpful feedback to user

### Example 3: Broad Topic

**Topic**: "Paris"

**Analysis**:
- Language: English
- Specificity: Broad
- Domain: General

**Alternative Terms Generated**:
1. "Paris organizations"
2. "Paris officials"
3. "Paris government"

**Agent Behavior**:
1. Searches "Paris" → May get too general results
2. Uses alternatives to focus on entity-rich content
3. Returns relevant organizations and officials

---

## Expected Improvements

### Quantitative Metrics

**Before Fallback Strategies**:
- Success Rate: 8.3% (4/48 extractions)
- German Topic Success: ~0%
- Very Specific Topic Success: ~0%

**Expected After Fallback Strategies**:
- Success Rate: >60% (target: 70%)
- German Topic Success: >50%
- Very Specific Topic Success: >40%

### Qualitative Improvements

1. **Better Coverage for Specific Topics**:
   - Topics with years now have fallback without year
   - Report-type topics broadened to core concepts
   - More entities found through alternative terms

2. **Improved User Experience**:
   - Helpful feedback when extraction fails
   - Suggestions for alternative searches
   - Clear explanation of why extraction failed

3. **More Persistent Search**:
   - Agents try multiple search terms before giving up
   - Combine results from multiple searches
   - Better coverage of topic landscape

---

## Testing

### Test Script

Use `tests/test_improved_prompts.py` to test fallback strategies:

```bash
# Start API server
poetry run python api/main.py

# Run tests
python tests/test_improved_prompts.py
```

### Test Cases

1. **Simple Topic**: "Paris France"
   - Should work without fallbacks
   - Tests baseline functionality

2. **German Government Topic**: "Jugendschutz Baden-Württemberg 2025"
   - Should use fallback (remove year)
   - Tests German + specificity handling

3. **German Social Topic**: "Jugendarmut Baden-Württemberg"
   - Should use domain-specific alternatives
   - Tests social domain handling

4. **Specific Official**: "Dr. Manfred Lucha Baden-Württemberg"
   - Should work with person search
   - Tests person entity extraction

---

## Limitations

### Known Limitations

1. **Tool Dependency**:
   - Still requires Tavily Search to work
   - If tool fails, fallbacks won't help
   - Need tool access monitoring

2. **Alternative Term Quality**:
   - Generated alternatives may not always be optimal
   - Some topics may need manual alternative terms
   - Could benefit from domain-specific dictionaries

3. **Language Mixing**:
   - Topics mixing German and English may be challenging
   - Alternatives prioritize one language
   - May miss entities in secondary language

4. **Very Niche Topics**:
   - Some topics truly have no online sources
   - Fallbacks can't create information that doesn't exist
   - Need to set user expectations

### Future Enhancements

1. **Machine Learning for Alternative Terms**:
   - Learn from successful searches
   - Build topic-specific alternative dictionaries
   - Improve alternative term quality

2. **Multiple Tool Fallbacks**:
   - Try Wikipedia if Tavily fails
   - Try Google Search as backup
   - Use Firecrawl for deep extraction

3. **User-Provided Alternatives**:
   - Allow users to suggest alternative terms
   - Learn from user feedback
   - Build knowledge base of effective alternatives

4. **Adaptive Strategy**:
   - Learn which strategies work for which topics
   - Adjust strategy based on success patterns
   - Optimize search order

---

## References

- Analysis Document: `docs/ENTITY_EXTRACTION_ANALYSIS.md`
- Prompt Improvements: `docs/PROMPT_IMPROVEMENTS.md`
- Test Script: `tests/test_improved_prompts.py`
- Implementation:
  - `api/search_strategy.py` - Core strategy logic
  - `api/agent_config.py` - Walking skeleton integration
  - `api/team_config.py` - Team agent integration
  - `api/main.py` - API feedback integration
- Requirements: 3.1, 4.2 (Research Capability, Entity Extraction)
