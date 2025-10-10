"""
Tests for team configuration module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from api.team_config import TeamConfig
from api.config import Config


def test_get_tools():
    """Test tool retrieval"""
    with patch('api.team_config.ToolFactory') as mock_tool_factory:
        mock_tool = Mock()
        mock_tool.id = "test_tool_id"
        mock_tool_factory.get.return_value = mock_tool
        
        tools = TeamConfig.get_tools()
        
        assert len(tools) == 1
        assert tools[0].id == "test_tool_id"
        mock_tool_factory.get.assert_called_once_with(Config.get_tool_id("tavily_search"))


def test_create_search_agent():
    """Test Search Agent creation"""
    with patch('api.team_config.AgentFactory') as mock_agent_factory, \
         patch('api.team_config.TeamConfig.get_tools') as mock_get_tools:
        
        # Mock tools
        mock_tool = Mock()
        mock_get_tools.return_value = [mock_tool]
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.id = "agent_123"
        mock_agent_factory.create.return_value = mock_agent
        
        # Create agent
        agent = TeamConfig.create_search_agent("Test Topic", model="testing")
        
        # Verify
        assert agent.id == "agent_123"
        mock_agent_factory.create.assert_called_once()
        
        # Check call arguments
        call_args = mock_agent_factory.create.call_args
        assert "name" in call_args.kwargs
        assert "Search Agent" in call_args.kwargs["name"]  # Updated: agent name doesn't include topic
        assert call_args.kwargs["llm_id"] == Config.get_model_id("testing")
        assert "tools" in call_args.kwargs


def test_create_team():
    """Test Team Agent creation"""
    with patch('api.team_config.TeamAgentFactory') as mock_team_factory, \
         patch('api.team_config.TeamConfig.create_search_agent') as mock_create_agent:
        
        # Mock search agent
        mock_search_agent = Mock()
        mock_search_agent.id = "search_agent_123"
        mock_create_agent.return_value = mock_search_agent
        
        # Mock team
        mock_team = Mock()
        mock_team.id = "team_123"
        mock_team_factory.create.return_value = mock_team
        
        # Create team
        team = TeamConfig.create_team(
            topic="Test Topic",
            goals=["Goal 1", "Goal 2"],
            model="testing"
        )
        
        # Verify
        assert team.id == "team_123"
        mock_create_agent.assert_called_once()
        mock_team_factory.create.assert_called_once()
        
        # Check call arguments
        call_args = mock_team_factory.create.call_args
        assert "name" in call_args.kwargs
        assert "Test Topic" in call_args.kwargs["name"]
        # Note: agents list may include Wikipedia agent too, so just check search agent is in there
        assert mock_search_agent in call_args.kwargs["agents"]
        assert call_args.kwargs["use_mentalist"] is True
        assert call_args.kwargs["use_inspector"] is True
        assert call_args.kwargs["inspector_targets"] == ["steps", "output"]  # Updated
        assert call_args.kwargs["llm_id"] == Config.get_model_id("testing")


def test_format_research_prompt():
    """Test research prompt formatting"""
    # Without goals
    prompt = TeamConfig.format_research_prompt("Test Topic")
    assert "Test Topic" in prompt
    assert "Person" in prompt
    assert "Organization" in prompt
    
    # With goals
    prompt = TeamConfig.format_research_prompt("Test Topic", ["Goal 1", "Goal 2"])
    assert "Test Topic" in prompt
    assert "Goal 1" in prompt
    assert "Goal 2" in prompt


def test_model_ids():
    """Test model ID configuration"""
    assert "testing" in Config.MODELS
    assert "production" in Config.MODELS
    assert Config.MODELS["testing"] == "669a63646eb56306647e1091"
    assert Config.MODELS["production"] == "6646261c6eb563165658bbb1"
    # Test default model
    assert Config.DEFAULT_MODEL == "production"
    assert Config.get_model_id() == Config.MODELS["production"]
    assert Config.get_model_id("testing") == Config.MODELS["testing"]


def test_tool_ids():
    """Test tool ID configuration"""
    assert "tavily_search" in Config.TOOL_IDS
    assert Config.TOOL_IDS["tavily_search"] == "6736411cf127849667606689"
    assert Config.get_tool_id("tavily_search") == "6736411cf127849667606689"
