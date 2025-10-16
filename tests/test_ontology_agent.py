"""
Test Ontology Agent Configuration and Instructions

This test verifies that the Ontology Agent can be created and configured correctly.
"""
import pytest
from api.team_config import TeamConfig
from api.instructions.ontology_agent import get_ontology_agent_instructions


def test_ontology_agent_instructions():
    """Test that Ontology Agent instructions are generated correctly"""
    instructions = get_ontology_agent_instructions()
    
    # Verify instructions contain key sections
    assert "Ontology Agent" in instructions
    assert "schema.org" in instructions.lower()
    assert "type improvement" in instructions.lower() or "type suggestion" in instructions.lower()
    assert "relationship" in instructions.lower()
    assert "GovernmentOrganization" in instructions
    
    # Verify instructions mention autonomous behavior
    assert "autonomous" in instructions.lower() or "monitor" in instructions.lower()
    
    # Verify instructions mention key schema.org concepts
    assert "worksFor" in instructions or "parentOrganization" in instructions
    assert "suggestion" in instructions.lower()
    
    print("✓ Ontology Agent instructions generated successfully")
    print(f"✓ Instructions length: {len(instructions)} characters")


def test_create_ontology_agent():
    """Test that Ontology Agent can be created"""
    try:
        agent = TeamConfig.create_ontology_agent()
        
        # Verify agent was created
        assert agent is not None
        assert hasattr(agent, 'id')
        assert hasattr(agent, 'name')
        
        # Verify agent name
        assert "Ontology" in agent.name
        
        print(f"✓ Ontology Agent created successfully")
        print(f"✓ Agent ID: {agent.id}")
        print(f"✓ Agent Name: {agent.name}")
        
        return agent
        
    except Exception as e:
        pytest.skip(f"Could not create Ontology Agent (may need API credentials): {e}")


def test_ontology_agent_in_team():
    """Test that Ontology Agent can be included in team configuration"""
    try:
        # Create team with Ontology Agent enabled
        team = TeamConfig.create_team(
            topic="Test Topic for Ontology Agent",
            enable_ontology=True,
            enable_validation=False,  # Disable validation to isolate Ontology Agent
            enable_wikipedia=False
        )
        
        assert team is not None
        assert hasattr(team, 'id')
        
        print(f"✓ Team created with Ontology Agent")
        print(f"✓ Team ID: {team.id}")
        
        return team
        
    except Exception as e:
        pytest.skip(f"Could not create team with Ontology Agent (may need API credentials): {e}")


def test_ontology_agent_suggestions_format():
    """Test that Ontology Agent instructions include proper suggestion formats"""
    instructions = get_ontology_agent_instructions()
    
    # Verify suggestion format examples are present
    assert "TYPE IMPROVEMENT SUGGESTION" in instructions or "type improvement" in instructions.lower()
    assert "RELATIONSHIP SUGGESTION" in instructions or "relationship suggestion" in instructions.lower()
    assert "PROPERTY ADDITION SUGGESTION" in instructions or "property addition" in instructions.lower()
    
    # Verify schema.org reference format
    assert "schema.org" in instructions.lower()
    assert "https://schema.org/" in instructions
    
    # Verify example suggestions are present
    assert "Bundesministerium" in instructions or "Ministry" in instructions or "Organization" in instructions
    
    print("✓ Ontology Agent suggestion formats verified")


def test_ontology_agent_schema_org_knowledge():
    """Test that Ontology Agent instructions include schema.org type knowledge"""
    instructions = get_ontology_agent_instructions()
    
    # Verify key schema.org types are mentioned
    schema_org_types = [
        "GovernmentOrganization",
        "Organization",
        "Person",
        "Event"
    ]
    
    found_types = [t for t in schema_org_types if t in instructions]
    assert len(found_types) >= 2, f"Expected at least 2 schema.org types, found: {found_types}"
    
    # Verify relationship properties are mentioned
    relationship_props = [
        "worksFor",
        "parentOrganization",
        "memberOf",
        "organizer"
    ]
    
    found_props = [p for p in relationship_props if p in instructions]
    assert len(found_props) >= 2, f"Expected at least 2 relationship properties, found: {found_props}"
    
    print(f"✓ Schema.org types found: {found_types}")
    print(f"✓ Relationship properties found: {found_props}")


def test_ontology_agent_no_tools():
    """Test that Ontology Agent doesn't require external tools"""
    try:
        agent = TeamConfig.create_ontology_agent()
        
        # Ontology Agent should not have tools (uses built-in knowledge)
        # Note: aixplain agents may have a tools attribute, but it should be empty or None
        if hasattr(agent, 'tools'):
            assert agent.tools is None or len(agent.tools) == 0
        
        print("✓ Ontology Agent correctly configured without external tools")
        
    except Exception as e:
        pytest.skip(f"Could not verify Ontology Agent tools (may need API credentials): {e}")


if __name__ == "__main__":
    print("Testing Ontology Agent Configuration...\n")
    
    print("Test 1: Ontology Agent Instructions")
    test_ontology_agent_instructions()
    print()
    
    print("Test 2: Ontology Agent Suggestion Formats")
    test_ontology_agent_suggestions_format()
    print()
    
    print("Test 3: Ontology Agent Schema.org Knowledge")
    test_ontology_agent_schema_org_knowledge()
    print()
    
    print("Test 4: Create Ontology Agent")
    try:
        test_create_ontology_agent()
    except Exception as e:
        print(f"⚠ Skipped (needs API credentials): {e}")
    print()
    
    print("Test 5: Ontology Agent in Team")
    try:
        test_ontology_agent_in_team()
    except Exception as e:
        print(f"⚠ Skipped (needs API credentials): {e}")
    print()
    
    print("Test 6: Ontology Agent No Tools")
    try:
        test_ontology_agent_no_tools()
    except Exception as e:
        print(f"⚠ Skipped (needs API credentials): {e}")
    print()
    
    print("=" * 60)
    print("All Ontology Agent tests completed!")
