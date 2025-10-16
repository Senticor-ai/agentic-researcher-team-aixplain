"""
Test Validation Agent Creation and Configuration

This test verifies that the Validation Agent can be created with validation tools
and has the correct configuration.
"""
import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from api.team_config import TeamConfig
from api.instructions.validation_agent import get_validation_agent_instructions

logger = logging.getLogger(__name__)


class TestValidationAgentInstructions:
    """Test Validation Agent instructions"""
    
    def test_get_validation_agent_instructions(self):
        """Test that validation agent instructions are generated correctly"""
        instructions = get_validation_agent_instructions()
        
        # Verify instructions contain key sections
        assert "Validation Agent" in instructions
        assert "Schema.org Validator tool" in instructions
        assert "URL Verifier tool" in instructions
        assert "ON-DEMAND VALIDATION" in instructions
        assert "PROACTIVE VALIDATION" in instructions
        
        # Verify validation workflow is described
        assert "SCHEMA.ORG VALIDATION" in instructions
        assert "URL VERIFICATION" in instructions
        assert "VALIDATION FEEDBACK" in instructions
        
        # Verify entity status values are defined
        assert "validated" in instructions
        assert "needs_sources" in instructions
        assert "needs_schema_review" in instructions
        assert "needs_wikipedia" in instructions
        
        # Verify metrics tracking is described
        assert "VALIDATION METRICS" in instructions
        assert "schema_org_compliance_rate" in instructions
        assert "url_validation_rate" in instructions
        assert "wikipedia_enrichment_rate" in instructions
        
        # Verify quality score calculation is described
        assert "QUALITY SCORE CALCULATION" in instructions
        assert "quality_score" in instructions
        
        logger.info("✓ Validation Agent instructions contain all required sections")
    
    def test_instructions_length(self):
        """Test that instructions are comprehensive"""
        instructions = get_validation_agent_instructions()
        
        # Instructions should be substantial (at least 2000 characters)
        assert len(instructions) > 2000
        
        logger.info(f"✓ Validation Agent instructions length: {len(instructions)} characters")


class TestValidationAgentCreation:
    """Test Validation Agent creation"""
    
    @patch('api.team_config.Config')
    @patch('api.team_config.ToolFactory')
    @patch('api.team_config.AgentFactory')
    def test_get_validation_tools(self, mock_agent_factory, mock_tool_factory, mock_config):
        """Test that validation tools can be retrieved"""
        # Mock tool objects
        mock_schema_tool = Mock()
        mock_schema_tool.id = "schema_validator_tool_id"
        mock_url_tool = Mock()
        mock_url_tool.id = "url_verifier_tool_id"
        
        # Mock Config.get_tool_id to return tool IDs
        def get_tool_id(tool_name):
            if tool_name == "schema_validator":
                return "schema_validator_tool_id"
            elif tool_name == "url_verifier":
                return "url_verifier_tool_id"
            raise KeyError(f"Unknown tool: {tool_name}")
        
        mock_config.get_tool_id.side_effect = get_tool_id
        
        # Mock ToolFactory.get to return tools
        def get_tool(tool_id):
            if tool_id == "schema_validator_tool_id":
                return mock_schema_tool
            elif tool_id == "url_verifier_tool_id":
                return mock_url_tool
            raise Exception(f"Unknown tool: {tool_id}")
        
        mock_tool_factory.get.side_effect = get_tool
        
        # Get validation tools
        tools = TeamConfig.get_validation_tools()
        
        # Verify tools were retrieved
        assert len(tools) == 2
        assert mock_schema_tool in tools
        assert mock_url_tool in tools
        
        logger.info("✓ Validation tools retrieved successfully")
    
    @patch('api.team_config.Config')
    @patch('api.team_config.ToolFactory')
    @patch('api.team_config.AgentFactory')
    def test_create_validation_agent(self, mock_agent_factory, mock_tool_factory, mock_config):
        """Test that Validation Agent can be created with tools"""
        # Mock tool objects
        mock_schema_tool = Mock()
        mock_schema_tool.id = "schema_validator_tool_id"
        mock_url_tool = Mock()
        mock_url_tool.id = "url_verifier_tool_id"
        
        # Mock Config.get_tool_id to return tool IDs
        def get_tool_id(tool_name):
            if tool_name == "schema_validator":
                return "schema_validator_tool_id"
            elif tool_name == "url_verifier":
                return "url_verifier_tool_id"
            raise KeyError(f"Unknown tool: {tool_name}")
        
        mock_config.get_tool_id.side_effect = get_tool_id
        
        # Mock ToolFactory.get to return tools
        def get_tool(tool_id):
            if tool_id == "schema_validator_tool_id":
                return mock_schema_tool
            elif tool_id == "url_verifier_tool_id":
                return mock_url_tool
            raise Exception(f"Unknown tool: {tool_id}")
        
        mock_tool_factory.get.side_effect = get_tool
        
        # Mock agent creation
        mock_agent = Mock()
        mock_agent.id = "validation_agent_id"
        mock_agent_factory.create.return_value = mock_agent
        
        # Create Validation Agent
        agent = TeamConfig.create_validation_agent()
        
        # Verify agent was created
        assert agent is not None
        assert agent.id == "validation_agent_id"
        
        # Verify AgentFactory.create was called with correct parameters
        mock_agent_factory.create.assert_called_once()
        call_kwargs = mock_agent_factory.create.call_args[1]
        
        assert call_kwargs["name"] == "Validation Agent"
        assert "quality checker" in call_kwargs["description"].lower()
        assert len(call_kwargs["tools"]) == 2
        assert mock_schema_tool in call_kwargs["tools"]
        assert mock_url_tool in call_kwargs["tools"]
        
        # Verify instructions contain validation logic
        instructions = call_kwargs["instructions"]
        assert "Schema.org Validator tool" in instructions
        assert "URL Verifier tool" in instructions
        assert "ON-DEMAND VALIDATION" in instructions
        
        logger.info("✓ Validation Agent created successfully with tools")
    
    @patch('api.team_config.ToolFactory')
    @patch('api.team_config.AgentFactory')
    def test_create_validation_agent_with_custom_model(self, mock_agent_factory, mock_tool_factory):
        """Test that Validation Agent can be created with custom model"""
        # Mock tool objects
        mock_schema_tool = Mock()
        mock_url_tool = Mock()
        
        mock_tool_factory.get.side_effect = [mock_schema_tool, mock_url_tool]
        
        # Mock agent creation
        mock_agent = Mock()
        mock_agent.id = "validation_agent_id"
        mock_agent_factory.create.return_value = mock_agent
        
        # Create Validation Agent with custom model
        custom_model_id = "custom_model_123"
        agent = TeamConfig.create_validation_agent(model_id=custom_model_id)
        
        # Verify agent was created with custom model
        assert agent is not None
        call_kwargs = mock_agent_factory.create.call_args[1]
        assert call_kwargs["llm_id"] == custom_model_id
        
        logger.info("✓ Validation Agent created with custom model")
    
    @patch('api.team_config.ToolFactory')
    @patch('api.team_config.AgentFactory')
    def test_create_validation_agent_no_tools(self, mock_agent_factory, mock_tool_factory):
        """Test that Validation Agent returns None if tools not available"""
        # Mock ToolFactory.get to raise exception (tools not found)
        mock_tool_factory.get.side_effect = Exception("Tool not found")
        
        # Try to create Validation Agent
        agent = TeamConfig.create_validation_agent()
        
        # Verify agent is None (cannot create without tools)
        assert agent is None
        
        # Verify AgentFactory.create was NOT called
        mock_agent_factory.create.assert_not_called()
        
        logger.info("✓ Validation Agent returns None when tools unavailable")


class TestValidationAgentIntegration:
    """Test Validation Agent integration scenarios"""
    
    def test_validation_agent_instructions_format(self):
        """Test that validation agent instructions follow expected format"""
        instructions = get_validation_agent_instructions()
        
        # Verify instructions describe on-demand validation
        assert "Search Agent calls you" in instructions
        assert "Wikipedia Agent calls you" in instructions
        assert "Orchestrator calls you" in instructions
        
        # Verify instructions describe proactive validation
        assert "Periodically scan" in instructions
        assert "broadcast to the hive mind" in instructions
        
        # Verify instructions describe validation workflow
        assert "SCHEMA.ORG VALIDATION" in instructions
        assert "URL VERIFICATION" in instructions
        
        # Verify instructions describe output format
        assert "VALIDATION OUTPUT FORMAT" in instructions
        assert "validation_status" in instructions
        assert "schema_org_valid" in instructions
        assert "url_validation" in instructions
        assert "quality_score" in instructions
        
        logger.info("✓ Validation Agent instructions follow expected format")
    
    def test_validation_metrics_in_instructions(self):
        """Test that validation metrics are properly described"""
        instructions = get_validation_agent_instructions()
        
        # Verify all required metrics are mentioned
        required_metrics = [
            "schema_org_compliance_rate",
            "url_validation_rate",
            "wikipedia_enrichment_rate",
            "quality_score"
        ]
        
        for metric in required_metrics:
            assert metric in instructions, f"Missing metric: {metric}"
        
        logger.info("✓ All validation metrics described in instructions")
    
    def test_entity_status_values_in_instructions(self):
        """Test that entity status values are defined"""
        instructions = get_validation_agent_instructions()
        
        # Verify all status values are defined
        status_values = [
            "validated",
            "needs_sources",
            "needs_schema_review",
            "needs_wikipedia",
            "validation_failed"
        ]
        
        for status in status_values:
            assert status in instructions, f"Missing status value: {status}"
        
        logger.info("✓ All entity status values defined in instructions")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])
