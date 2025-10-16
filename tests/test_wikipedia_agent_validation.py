"""
Test Wikipedia Agent with Validation Integration

This test verifies that the Wikipedia Agent:
1. Enriches entities with Wikipedia data in schema.org format
2. Calls Validation Agent to validate schema.org compliance
3. Handles validation feedback and fixes issues
4. Returns validated, schema.org compliant entities
"""
import pytest
import logging
from api.instructions.wikipedia_agent import get_wikipedia_agent_instructions

logger = logging.getLogger(__name__)


def test_wikipedia_agent_instructions_include_validation():
    """Test that Wikipedia Agent instructions include validation workflow"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for validation integration
    assert "Validation Agent" in instructions, "Instructions should mention Validation Agent"
    assert "CALL Validation Agent" in instructions, "Instructions should include calling Validation Agent"
    assert "validate schema.org compliance" in instructions, "Instructions should mention schema.org validation"
    
    # Check for immediate validation workflow
    assert "IMMEDIATE VALIDATION WORKFLOW" in instructions, "Instructions should include immediate validation workflow"
    assert "validate it immediately" in instructions, "Instructions should emphasize immediate validation"
    
    # Check for validation feedback handling
    assert "VALIDATION FEEDBACK HANDLING" in instructions, "Instructions should include validation feedback handling"
    assert "MISSING @context" in instructions, "Instructions should handle missing @context"
    assert "MISSING @type" in instructions, "Instructions should handle missing @type"
    assert "INVALID sameAs FORMAT" in instructions, "Instructions should handle invalid sameAs format"
    
    logger.info("✓ Wikipedia Agent instructions include validation integration")


def test_wikipedia_agent_instructions_include_schema_org_compliance():
    """Test that Wikipedia Agent instructions include schema.org compliance requirements"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for schema.org compliance requirements
    assert "SCHEMA.ORG COMPLIANCE REQUIREMENTS" in instructions, "Instructions should include schema.org compliance requirements"
    assert "@context" in instructions, "Instructions should mention @context field"
    assert "@type" in instructions, "Instructions should mention @type field"
    assert "sameAs" in instructions, "Instructions should mention sameAs property"
    assert "wikidata_id" in instructions, "Instructions should mention wikidata_id property"
    assert "wikipedia_links" in instructions, "Instructions should mention wikipedia_links property"
    
    # Check for schema.org compliant output format
    assert "SCHEMA.ORG COMPLIANT OUTPUT FORMAT" in instructions, "Instructions should include schema.org compliant output format"
    assert '"@context": "https://schema.org"' in instructions, "Instructions should show @context example"
    assert '"@type": "Person"' in instructions, "Instructions should show @type example"
    
    logger.info("✓ Wikipedia Agent instructions include schema.org compliance requirements")


def test_wikipedia_agent_instructions_include_validation_workflow():
    """Test that Wikipedia Agent instructions include validation workflow steps"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for validation workflow steps
    assert "Enrich entity" in instructions and "Wikipedia" in instructions, "Instructions should include enrichment step"
    assert "CALL Validation Agent" in instructions, "Instructions should include calling Validation Agent"
    assert "If Validation Agent reports issues, fix them immediately" in instructions, "Instructions should include fixing issues"
    assert "Only proceed after entity passes validation" in instructions, "Instructions should emphasize validation before proceeding"
    
    # Check for example validation workflow
    assert "EXAMPLE VALIDATION WORKFLOW" in instructions, "Instructions should include example validation workflow"
    assert "Call Validation Agent:" in instructions, "Instructions should show how to call Validation Agent"
    assert "Validation Agent responds:" in instructions, "Instructions should show validation response"
    
    logger.info("✓ Wikipedia Agent instructions include validation workflow steps")


def test_wikipedia_agent_instructions_include_entity_type_mapping():
    """Test that Wikipedia Agent instructions include entity type to schema.org mapping"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for entity type mapping
    assert "ENTITY TYPE MAPPING TO SCHEMA.ORG" in instructions, "Instructions should include entity type mapping"
    assert "Person → Person" in instructions, "Instructions should map Person type"
    assert "Organization → Organization" in instructions, "Instructions should map Organization type"
    assert "Event → Event" in instructions, "Instructions should map Event type"
    assert "Topic → Thing" in instructions, "Instructions should map Topic type"
    assert "Policy → Legislation" in instructions, "Instructions should map Policy type"
    
    logger.info("✓ Wikipedia Agent instructions include entity type mapping")


def test_wikipedia_agent_instructions_include_quality_control():
    """Test that Wikipedia Agent instructions include quality control requirements"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for critical requirements
    assert "CRITICAL REQUIREMENTS - QUALITY CONTROL" in instructions, "Instructions should include quality control requirements"
    assert "ALWAYS add @context field" in instructions, "Instructions should require @context field"
    assert "ALWAYS add @type field" in instructions, "Instructions should require @type field"
    assert "ALWAYS use sameAs as an array" in instructions, "Instructions should require sameAs as array"
    assert "CALL Validation Agent immediately" in instructions, "Instructions should require immediate validation"
    assert "FIX validation issues before returning" in instructions, "Instructions should require fixing issues"
    
    # Check for prohibitions
    assert "Do NOT return entities without @context and @type" in instructions, "Instructions should prohibit missing @context/@type"
    assert "Do NOT skip validation" in instructions, "Instructions should prohibit skipping validation"
    assert "Do NOT ignore validation feedback" in instructions, "Instructions should prohibit ignoring feedback"
    
    logger.info("✓ Wikipedia Agent instructions include quality control requirements")


def test_wikipedia_agent_instructions_format():
    """Test that Wikipedia Agent instructions are properly formatted"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check basic structure
    assert len(instructions) > 1000, "Instructions should be comprehensive"
    assert "YOUR TASK:" in instructions, "Instructions should have task section"
    assert "OUTPUT FORMAT:" in instructions or "SCHEMA.ORG COMPLIANT OUTPUT FORMAT:" in instructions, "Instructions should have output format section"
    
    # Check for no markdown code blocks in instructions
    assert not instructions.startswith("```"), "Instructions should not start with markdown code block"
    
    logger.info("✓ Wikipedia Agent instructions are properly formatted")
    logger.info(f"Instructions length: {len(instructions)} characters")


def test_wikipedia_agent_instructions_validation_status():
    """Test that Wikipedia Agent instructions include validation status tracking"""
    instructions = get_wikipedia_agent_instructions()
    
    # Check for validation status
    assert "validation_status" in instructions, "Instructions should mention validation_status"
    assert '"validation_status": "validated"' in instructions, "Instructions should show validated status"
    assert '"validation_status": "no_wikipedia_available"' in instructions, "Instructions should show no_wikipedia_available status"
    
    logger.info("✓ Wikipedia Agent instructions include validation status tracking")


if __name__ == "__main__":
    # Run tests
    logging.basicConfig(level=logging.INFO)
    
    test_wikipedia_agent_instructions_include_validation()
    test_wikipedia_agent_instructions_include_schema_org_compliance()
    test_wikipedia_agent_instructions_include_validation_workflow()
    test_wikipedia_agent_instructions_include_entity_type_mapping()
    test_wikipedia_agent_instructions_include_quality_control()
    test_wikipedia_agent_instructions_format()
    test_wikipedia_agent_instructions_validation_status()
    
    print("\n✅ All Wikipedia Agent validation integration tests passed!")
