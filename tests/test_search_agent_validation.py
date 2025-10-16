"""
Test Search Agent integration with Validation Agent

This test verifies that:
1. Search Agent instructions include validation workflow
2. Team configuration includes Validation Agent
3. Search Agent can call Validation Agent
4. Validation feedback is handled properly
"""
import pytest
from api.team_config import TeamConfig
from api.instructions.search_agent import get_search_agent_instructions


def test_search_agent_instructions_include_validation():
    """Test that Search Agent instructions include validation workflow"""
    topic = "Test Topic"
    instructions = get_search_agent_instructions(topic)
    
    # Check for validation-related content
    assert "Validation Agent" in instructions, "Instructions should mention Validation Agent"
    assert "IMMEDIATE VALIDATION WORKFLOW" in instructions, "Instructions should include validation workflow"
    assert "validate URLs" in instructions.lower(), "Instructions should mention URL validation"
    assert "validation feedback" in instructions.lower(), "Instructions should mention validation feedback"
    assert "fix them immediately" in instructions.lower(), "Instructions should mention fixing validation issues"
    
    # Check for validation feedback handling
    assert "VALIDATION FEEDBACK HANDLING" in instructions, "Instructions should include feedback handling section"
    assert "INVALID URL FORMAT" in instructions, "Instructions should cover invalid URL handling"
    assert "INACCESSIBLE URL" in instructions, "Instructions should cover inaccessible URL handling"
    assert "LOW-QUALITY SOURCES" in instructions, "Instructions should cover low-quality source handling"
    
    # Check for validation workflow example
    assert "EXAMPLE VALIDATION WORKFLOW" in instructions, "Instructions should include validation workflow example"
    assert "Call Validation Agent" in instructions, "Instructions should show how to call Validation Agent"


def test_team_includes_validation_agent():
    """Test that team configuration includes Validation Agent when enabled"""
    topic = "Test Topic"
    
    # Create team with validation enabled (default)
    team = TeamConfig.create_team(topic, enable_validation=True)
    
    # Team should be created successfully
    assert team is not None, "Team should be created"
    assert hasattr(team, 'id'), "Team should have an ID"
    
    # Note: We can't directly check if Validation Agent is in the team
    # because aixplain's TeamAgent doesn't expose the agents list
    # But we can verify the team was created without errors


def test_team_without_validation_agent():
    """Test that team can be created without Validation Agent"""
    topic = "Test Topic"
    
    # Create team with validation disabled
    team = TeamConfig.create_team(topic, enable_validation=False)
    
    # Team should be created successfully
    assert team is not None, "Team should be created"
    assert hasattr(team, 'id'), "Team should have an ID"


def test_validation_agent_creation():
    """Test that Validation Agent can be created independently"""
    validation_agent = TeamConfig.create_validation_agent()
    
    # Agent should be created if validation tools are available
    # If tools are not available, agent will be None
    if validation_agent is not None:
        assert hasattr(validation_agent, 'id'), "Validation Agent should have an ID"
        assert hasattr(validation_agent, 'name'), "Validation Agent should have a name"
        assert validation_agent.name == "Validation Agent", "Agent name should be 'Validation Agent'"


def test_search_agent_validation_quality_control():
    """Test that Search Agent instructions include validation quality control"""
    topic = "Test Topic"
    instructions = get_search_agent_instructions(topic)
    
    # Check for validation in quality control section
    quality_control_section = instructions[instructions.find("CRITICAL REQUIREMENTS - QUALITY CONTROL"):]
    
    assert "CALL Validation Agent immediately" in quality_control_section, \
        "Quality control should require calling Validation Agent"
    assert "FIX validation issues" in quality_control_section, \
        "Quality control should require fixing validation issues"
    assert "Track validation status" in quality_control_section, \
        "Quality control should require tracking validation status"
    assert "Do NOT skip validation" in quality_control_section, \
        "Quality control should prohibit skipping validation"
    assert "Do NOT ignore validation feedback" in quality_control_section, \
        "Quality control should prohibit ignoring validation feedback"


def test_search_agent_validation_workflow_steps():
    """Test that Search Agent instructions include detailed validation workflow steps"""
    topic = "Test Topic"
    instructions = get_search_agent_instructions(topic)
    
    # Find the validation workflow section
    workflow_start = instructions.find("IMMEDIATE VALIDATION WORKFLOW")
    workflow_section = instructions[workflow_start:workflow_start + 1000]
    
    # Check for key workflow steps
    assert "Extract entities from search results" in workflow_section, \
        "Workflow should include entity extraction step"
    assert "CALL Validation Agent" in workflow_section, \
        "Workflow should include calling Validation Agent"
    assert "If Validation Agent reports invalid URLs" in workflow_section, \
        "Workflow should include handling invalid URLs"
    assert "improve the entity by finding better sources" in workflow_section, \
        "Workflow should include improving sources"
    assert "Only proceed to next entity after current entity is validated" in workflow_section, \
        "Workflow should require validation before proceeding"


def test_search_agent_validation_integration_description():
    """Test that Search Agent instructions describe Validation Agent integration"""
    topic = "Test Topic"
    instructions = get_search_agent_instructions(topic)
    
    # Find the validation agent integration section
    integration_start = instructions.find("VALIDATION AGENT INTEGRATION")
    integration_section = instructions[integration_start:integration_start + 1000]
    
    # Check for integration details
    assert "peer" in integration_section.lower(), \
        "Integration should describe Validation Agent as a peer"
    assert "call it anytime" in integration_section.lower(), \
        "Integration should allow calling anytime"
    assert "Wait for validation feedback" in integration_section, \
        "Integration should require waiting for feedback"
    assert "fix them immediately" in integration_section.lower(), \
        "Integration should require immediate fixes"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
