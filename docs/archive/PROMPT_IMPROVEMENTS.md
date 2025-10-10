# Entity Extraction Prompt Improvements

## Overview

This document describes the improvements made to agent prompts to address entity extraction failures identified in the analysis (see `ENTITY_EXTRACTION_ANALYSIS.md`).

**Date**: 2025-10-09  
**Task**: 9.2 - Refine Search Agent prompts for better extraction  
**Files Modified**:
- `api/agent_config.py` - Walking skeleton agent configuration
- `api/team_config.py` - Team agent configuration (Search Agent and Mentalist)

---

## Key Improvements

### 1. German Language Support

**Problem**: German topics consistently failed to extract entities (91.7% failure rate).

**Solution**: Added explicit German language instructions to agent prompts.

**Changes**:
```
LANGUAGE SUPPORT:
- Search for information in BOTH English AND German
- For German topics, prioritize German-language sources (.de domains, German government sites)
- Include entities from German sources with German descriptions
- Accept sources in any language that contain relevant information
```

**Impact**:
- Agents now explicitly search German sources for German topics
- Prioritizes .de domains and German government sites
- Accepts German entity names and descriptions

### 2. Real Source URL Requirement

**Problem**: Successful extractions had placeholder URLs (example.com), indicating fabricated data.

**Solution**: Added strict requirements for real source URLs.

**Changes**:
```
CRITICAL REQUIREMENTS:
- Use REAL URLs from Tavily search results (never use example.com or placeholder URLs)
- Include actual excerpts from the sources
- If you find no relevant entities, return: {"entities": []}
- Do NOT invent or fabricate entities - only extract what you actually find
```

**Impact**:
- Agents must use actual URLs from Tavily results
- Reduces fabricated/hallucinated entities
- Improves data quality and trustworthiness

### 3. Successful Extraction Examples

**Problem**: Agents lacked clear examples of what successful extraction looks like.

**Solution**: Added concrete examples in the prompt.

**Examples Added**:

**Example 1 - German Government Official**:
```json
{
  "type": "Person",
  "name": "Dr. Manfred Lucha",
  "description": "Minister für Soziales, Gesundheit und Integration Baden-Württemberg",
  "jobTitle": "Minister",
  "sources": [{"url": "https://sozialministerium.baden-wuerttemberg.de/...", "excerpt": "..."}]
}
```

**Example 2 - German Ministry**:
```json
{
  "type": "Organization",
  "name": "Ministerium für Soziales, Gesundheit und Integration Baden-Württemberg",
  "description": "State ministry responsible for social affairs, health and integration",
  "sources": [{"url": "https://sozialministerium.baden-wuerttemberg.de/", "excerpt": "..."}]
}
```

**Example 3 - NGO**:
```json
{
  "type": "Organization",
  "name": "Caritas Baden-Württemberg",
  "description": "Catholic welfare organization providing social services",
  "sources": [{"url": "https://www.caritas-dicv-fr.de/", "excerpt": "..."}]
}
```

**Impact**:
- Provides clear templates for entity extraction
- Shows expected format and level of detail
- Demonstrates German language entities

### 4. Domain-Specific Guidance

**Problem**: Agents didn't know what types of entities to look for in government/social topics.

**Solution**: Added specific guidance for different domains.

**Changes**:
```
ENTITY EXTRACTION GUIDELINES:
- For German government topics, look for: ministers, state secretaries, department heads, agencies
- For social topics, look for: NGOs, welfare organizations, advocacy groups
```

**Impact**:
- Agents know what entity types are relevant
- Improves recall for domain-specific entities
- Better coverage of stakeholder landscape

### 5. Enhanced Mentalist Instructions

**Problem**: Mentalist didn't coordinate Search Agent effectively for German topics.

**Solution**: Updated Mentalist instructions with language-aware strategy.

**Changes**:
```
LANGUAGE HANDLING:
- For German topics (e.g., "Jugendarmut Baden-Württemberg"), instruct Search Agent to:
  - Search in German language
  - Prioritize .de domains and German government sites
  - Extract entities with German names and descriptions
```

**Impact**:
- Mentalist now adapts strategy based on topic language
- Better coordination for German research
- More effective use of Search Agent capabilities

### 6. Quality Requirements and Failure Mode Awareness

**Problem**: Agents didn't understand quality standards or common pitfalls.

**Solution**: Added explicit quality requirements and failure mode warnings.

**Changes**:
```
QUALITY REQUIREMENTS:
- All entities must have REAL source citations (URL + excerpt from actual sources)
- Reject entities with placeholder URLs (example.com, test.com, etc.)
- Focus on authoritative sources (government sites, official pages, reputable news)

COMMON FAILURE MODES TO AVOID:
- Do NOT accept fabricated entities without real sources
- Do NOT accept placeholder URLs (example.com)
- Do NOT skip German-language sources for German topics
- Do NOT give up after one search - try alternative terms if needed
```

**Impact**:
- Agents understand quality standards
- Aware of common mistakes to avoid
- More persistent in finding real information

---

## Testing Strategy

### Test Cases

Created `tests/test_improved_prompts.py` with 4 test cases:

1. **Simple Well-Known Topic**: "Paris France"
   - Expected: ≥3 entities
   - Tests: Basic functionality with easy topic

2. **German Government Topic**: "Jugendschutz Baden-Württemberg 2025"
   - Expected: ≥2 entities
   - Tests: German language support, government domain

3. **German Social Topic**: "Jugendarmut Baden-Württemberg"
   - Expected: ≥3 entities
   - Tests: Real source requirement (previously had placeholders)

4. **Specific German Official**: "Dr. Manfred Lucha Baden-Württemberg"
   - Expected: ≥2 entities
   - Tests: Person search, German official

### Success Criteria

For each test:
- ✅ **Pass**: Meets minimum entity count AND no placeholder URLs
- ⚠️ **Partial Pass**: Meets minimum entity count BUT has placeholder URLs
- ✗ **Fail**: Below minimum entity count OR extraction failed

### Running Tests

```bash
# Start API server
poetry run python api/main.py

# In another terminal, run tests
python tests/test_improved_prompts.py
```

Results saved to: `tests/improved_prompts_test_results.json`

---

## Expected Improvements

### Quantitative Metrics

**Before Improvements**:
- Success Rate: 8.3% (4/48 extractions)
- German Topic Success: ~0% (all failed)
- Placeholder URL Rate: 100% (of successful extractions)

**Expected After Improvements**:
- Success Rate: >50% (target: 60-70%)
- German Topic Success: >40% (target: 50%)
- Placeholder URL Rate: <10% (target: 0%)

### Qualitative Improvements

1. **Better German Coverage**:
   - Extract entities from German government sites
   - Include German NGOs and welfare organizations
   - Capture German official names and titles

2. **Higher Data Quality**:
   - Real source URLs from authoritative sites
   - Actual excerpts from sources
   - Verifiable entity information

3. **More Relevant Entities**:
   - Domain-appropriate entity types
   - Key stakeholders for policy topics
   - Officials and organizations with clear roles

---

## Limitations and Future Work

### Known Limitations

1. **Tool Dependency**: Still relies on Tavily Search tool access
   - If tool fails, extraction fails
   - No fallback search mechanism yet

2. **Niche Topics**: Very specific topics may still fail
   - Limited online sources for administrative topics
   - Information in non-crawlable formats (PDFs)

3. **Language Mixing**: Topics mixing German and English may be challenging
   - Prompt prioritizes one language
   - May miss entities in secondary language

### Future Improvements (Task 9.3)

1. **Multi-Pass Search Strategy**:
   - Start with broader search terms
   - Narrow down based on initial results
   - Try alternative phrasings

2. **Fallback Tools**:
   - Add Wikipedia for entity verification
   - Add Google Search as backup
   - Add Firecrawl for deep website extraction

3. **Better Error Handling**:
   - Distinguish "no results" from "tool failure"
   - Provide actionable feedback to users
   - Suggest alternative search terms

---

## Validation Checklist

Before considering this task complete:

- [x] Updated agent prompts with German language support
- [x] Added real source URL requirements
- [x] Included successful extraction examples
- [x] Added domain-specific guidance
- [x] Enhanced Mentalist instructions
- [x] Created test script with 4 test cases
- [x] Documented improvements and expected impact
- [ ] Run tests and verify improvements (requires API server)
- [ ] Update analysis document with new results

---

## References

- Analysis Document: `docs/ENTITY_EXTRACTION_ANALYSIS.md`
- Test Script: `tests/test_improved_prompts.py`
- Modified Files:
  - `api/agent_config.py`
  - `api/team_config.py`
- Requirements: 4.1, 4.2 (Entity Extraction)
