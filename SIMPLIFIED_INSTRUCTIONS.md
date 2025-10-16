# Simplified Mentalist Instructions

## Changes Made

### Problem
The Mentalist instructions were extremely verbose (over 500 lines) with:
- Detailed JSON-LD examples
- Extensive MECE decomposition documentation
- Multiple search strategy patterns
- Redundant explanations

This could be overwhelming the LLM and causing execution failures.

### Solution
Drastically simplified the Mentalist instructions to high-level guidance:

**Before:** ~500 lines with detailed examples
**After:** ~50 lines with core concepts

### What Was Removed

1. **Detailed JSON-LD Examples**
   - Removed all schema.org structure examples
   - Removed entity format specifications
   - Response Generator handles formatting, not Mentalist

2. **Verbose MECE Documentation**
   - Removed detailed MECE decomposition examples
   - Removed step-by-step workflows
   - Kept only high-level concept

3. **Extensive Search Patterns**
   - Removed detailed search term variations
   - Removed round-by-round strategies
   - Kept simple multi-round approach

4. **Redundant Warnings**
   - Removed repeated "DO NOT" warnings
   - Removed failure mode examples
   - Kept only critical rules

### What Was Kept

1. **Core Role**
   - Plan research strategy
   - Coordinate Search Agent
   - Track progress

2. **Critical Rules**
   - Never assign tasks to yourself
   - Always assign search to Search Agent
   - Use full interaction budget
   - Continue until comprehensive coverage

3. **Available Agents**
   - Search Agent (with tools)
   - Wikipedia Agent (if enabled)
   - Validation Agent (if enabled)
   - Ontology Agent (if enabled)

4. **Quality Requirements**
   - Real source citations
   - Authoritative sources
   - German sources for German topics

### Inspector Configuration

Added brief instructions to Inspector:
```python
inspector_instructions = """Review agent outputs for:
1. Entity quality - Do entities have real source URLs?
2. Coverage - Are multiple entity types represented?
3. Relevance - Are entities related to the research topic?

Provide brief, actionable feedback if issues found."""
```

## Expected Benefits

1. **Reduced Token Usage**
   - Shorter instructions = fewer tokens per request
   - More budget for actual research

2. **Clearer Focus**
   - LLM can focus on core responsibilities
   - Less chance of confusion or misinterpretation

3. **Faster Processing**
   - Less text to process
   - Quicker decision-making

4. **Better Execution**
   - Simpler instructions = more reliable execution
   - Less chance of getting stuck on complex rules

## Testing

To test the simplified instructions:

```bash
# Create a new team via API/UI
# Topic: "Familienforum Markdorf"
# Check if execution completes successfully
```

Compare with previous executions:
- Check server logs for errors
- Verify entities are extracted
- Review intermediate steps count

## Rollback Plan

If simplified instructions cause issues, the original verbose version is in git history:
```bash
git log api/instructions/mentalist.py
git show <commit>:api/instructions/mentalist.py
```

## Next Steps

1. Test with a new team execution
2. Monitor server logs for improvements
3. Check if entities are extracted successfully
4. If still failing, investigate team coordination issues (not instruction length)
