"""
Tests for aixplain agent integration (V1 - DEPRECATED)

These tests are for the old single-agent architecture.
See test_team_config.py for V2 team agent tests.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# V1 tests - skipping as we've moved to V2 team agent architecture
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skip(reason="V1 single agent tests deprecated - see test_team_config.py for V2")
]


def test_walking_skeleton_config():
    """Test that walking skeleton config is properly structured"""
    topic = "Dr. Manfred Lucha biography"
    config = AgentConfig.get_walking_skeleton_config(topic, model="testing")
    
    # Verify config structure
    assert "name" in config
    assert "description" in config
    assert "llm_id" in config
    assert "system_prompt" in config
    assert "tools" in config
    
    # Verify model selection
    assert config["llm_id"] == "gpt-4o-mini"
    
    # Verify tools are included
    assert len(config["tools"]) > 0
    
    # Verify topic is in system prompt
    assert topic in config["system_prompt"]


def test_format_research_prompt():
    """Test research prompt formatting"""
    topic = "Integration policies in Baden-Württemberg"
    goals = ["Identify key stakeholders", "Timeline of policy changes"]
    
    prompt = AgentConfig.format_research_prompt(topic, goals)
    
    # Verify topic is included
    assert topic in prompt
    
    # Verify goals are included
    for goal in goals:
        assert goal in prompt
    
    # Verify instructions are included
    assert "Person entities" in prompt
    assert "Organization entities" in prompt


def test_format_research_prompt_without_goals():
    """Test research prompt formatting without goals"""
    topic = "Test topic"
    
    prompt = AgentConfig.format_research_prompt(topic)
    
    # Verify topic is included
    assert topic in prompt
    
    # Verify basic structure
    assert "Person entities" in prompt
    assert "Organization entities" in prompt


@patch('api.aixplain_client.AgentFactory')
def test_agent_client_create_agent(mock_factory):
    """Test agent creation logic (mocked)"""
    from api.aixplain_client import AgentClient
    
    # Mock the agent creation
    mock_agent = Mock()
    mock_agent.id = "test-agent-123"
    mock_factory.create.return_value = mock_agent
    
    # Create client (will fail on real API key validation, so we mock it)
    with patch('api.aixplain_client.get_settings') as mock_settings:
        mock_settings.return_value.aixplain_api_key = "test-key"
        client = AgentClient(api_key="test-key")
        
        # Create agent
        agent = client.create_agent(
            name="Test Agent",
            description="Test Description",
            llm_id="gpt-4o-mini",
            system_prompt="Test prompt",
            tools=[]
        )
        
        # Verify agent was created
        assert agent.id == "test-agent-123"
        mock_factory.create.assert_called_once()


@patch('api.aixplain_client.AgentFactory')
def test_agent_client_run_agent(mock_factory):
    """Test agent execution logic (mocked)"""
    from api.aixplain_client import AgentClient
    
    # Mock the agent
    mock_agent = Mock()
    mock_agent.id = "test-agent-123"
    mock_agent.run.return_value = {
        'data': 'Test response',
        'status': 'completed'
    }
    
    # Create client
    with patch('api.aixplain_client.get_settings') as mock_settings:
        mock_settings.return_value.aixplain_api_key = "test-key"
        client = AgentClient(api_key="test-key")
        
        # Run agent
        result = client.run_agent(mock_agent, "Test input")
        
        # Verify result structure
        assert 'output' in result
        assert 'status' in result
        assert 'agent_id' in result
        assert result['output'] == 'Test response'
        assert result['status'] == 'completed'
        assert result['agent_id'] == "test-agent-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
