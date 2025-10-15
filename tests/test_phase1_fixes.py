"""
TDD Tests for Phase 1 Quick Fixes

Tests verify the changes made to address Search Agent timeout issues:
1. Search Agent defaults to GPT-4o (production model)
2. Tavily Search best practices added to instructions
3. Search Agent responsibility simplified (no compilation)
4. Mentalist instructions updated (don't ask Search Agent to compile)
5. Debug logging added for model and interaction limit
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from api.team_config import TeamConfig
from api.config import Config
from api.instructions.search_agent import get_search_agent_instructions
from api.instructions.mentalist import get_mentalist_instructions

pytestmark = pytest.mark.unit


class TestSearchAgentModelDefault:
    """Test that Search Agent defaults to GPT-4o (production model)"""
    
    def test_search_agent_defaults_to_gpt4o(self):
        """Search Agent should use GPT-4o by default"""
        with patch('api.team_config.AgentFactory') as mock_agent_factory, \
             patch('api.team_config.TeamConfig.get_tools') as mock_get_tools:
            
            # Mock tools
            mock_tool = Mock()
            mock_get_tools.return_value = [mock_tool]
            
            # Mock agent
            mock_agent = Mock()
            mock_agent.id = "agent_123"
            mock_agent_factory.create.return_value = mock_agent
            
            # Create agent WITHOUT specifying model (should default to GPT-4o)
            agent = TeamConfig.create_search_agent("Test Topic")
            
            # Verify GPT-4o was used
            call_args = mock_agent_factory.create.call_args
            assert call_args.kwargs["llm_id"] == Config.SEARCH_AGENT_MODEL
            assert call_args.kwargs["llm_id"] == Config.GPT_4O
    
    def test_search_agent_can_override_model(self):
        """Search Agent should allow model override if explicitly specified"""
        with patch('api.team_config.AgentFactory') as mock_agent_factory, \
             patch('api.team_config.TeamConfig.get_tools') as mock_get_tools:
            
            # Mock tools
            mock_tool = Mock()
            mock_get_tools.return_value = [mock_tool]
            
            # Mock agent
            mock_agent = Mock()
            mock_agent.id = "agent_123"
            mock_agent_factory.create.return_value = mock_agent
            
            # Create agent with explicit model ID
            custom_model_id = "custom_model_123"
            agent = TeamConfig.create_search_agent("Test Topic", model_id=custom_model_id)
            
            # Verify custom model was used
            call_args = mock_agent_factory.create.call_args
            assert call_args.kwargs["llm_id"] == custom_model_id
    
    def test_gpt4o_model_configured(self):
        """Verify GPT-4o model ID is configured"""
        assert Config.GPT_4O == "6646261c6eb563165658bbb1"
    
    def test_agent_models_configured(self):
        """Verify all agent models are configured to GPT-4o"""
        assert Config.SEARCH_AGENT_MODEL == Config.GPT_4O
        assert Config.WIKIPEDIA_AGENT_MODEL == Config.GPT_4O
        assert Config.TEAM_AGENT_MODEL == Config.GPT_4O


class TestTavilyBestPractices:
    """Test that Tavily Search best practices are in instructions"""
    
    def test_tavily_best_practices_section_exists(self):
        """Instructions should include TAVILY SEARCH BEST PRACTICES section"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "TAVILY SEARCH BEST PRACTICES:" in instructions
    
    def test_specific_query_guidance(self):
        """Instructions should explain how to craft specific queries"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "CRAFT SPECIFIC QUERIES:" in instructions
        assert "Manfred Lucha Minister Baden-Württemberg" in instructions
    
    def test_form_filtering_guidance(self):
        """Instructions should explain how to filter out quiz/form pages"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "FILTER OUT NON-CONTENT PAGES:" in instructions
        assert "Wählen Sie" in instructions  # German quiz indicator
        assert "Frage 1, Frage 2" in instructions  # Test questions
    
    def test_german_search_term_guidance(self):
        """Instructions should explain to use German terms for German topics"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "FOR GERMAN TOPICS - USE GERMAN SEARCH TERMS:" in instructions
        assert "Ministerium" in instructions
        assert "Behörde" in instructions
        assert "site:.de" in instructions
    
    def test_quiz_handling_guidance(self):
        """Instructions should explain what to do if Tavily returns forms/quizzes"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "IF TAVILY RETURNS FORMS/QUIZZES" in instructions
        assert "Try more specific search terms" in instructions
        assert "Use Google Search as backup" in instructions
    
    def test_result_validation_guidance(self):
        """Instructions should explain how to validate results before extraction"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "RESULT VALIDATION BEFORE EXTRACTION:" in instructions
        assert "Check if result is an article" in instructions


class TestSearchAgentResponsibility:
    """Test that Search Agent responsibility is simplified"""
    
    def test_single_responsibility_statement_exists(self):
        """Instructions should clearly state Search Agent's single responsibility"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "YOUR SINGLE RESPONSIBILITY:" in instructions
        assert "DO NOT compile reports" in instructions
    
    def test_no_compilation_instruction(self):
        """Instructions should explicitly say not to compile reports"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "DO NOT compile reports or create summaries" in instructions
        assert "Response Generator will handle compilation" in instructions
    
    def test_old_extraction_summary_removed(self):
        """Old EXTRACTION SUMMARY section should be removed"""
        instructions = get_search_agent_instructions("Test Topic")
        
        # Check that old detailed summary is NOT present
        assert not ("Total entities extracted: [number]" in instructions and 
                   "By type: Person: [X], Organization: [X]" in instructions)
    
    def test_simplified_notes_section_exists(self):
        """New simplified SEARCH EFFECTIVENESS NOTES should exist"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "SEARCH EFFECTIVENESS NOTES:" in instructions
        assert "Keep notes brief" in instructions


class TestMentalistInstructions:
    """Test that Mentalist instructions clarify Search Agent role"""
    
    def test_search_agent_role_clarification_exists(self):
        """Mentalist instructions should clarify Search Agent only searches/extracts"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert "IMPORTANT: Search Agent only searches and extracts" in instructions
        assert "does NOT compile reports" in instructions
    
    def test_response_generator_responsibility_clarified(self):
        """Mentalist instructions should clarify Response Generator handles compilation"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert "Response Generator's responsibility" in instructions
    
    def test_good_task_examples_provided(self):
        """Mentalist instructions should provide examples of good tasks"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert '✓ "Search for ministers' in instructions
        assert '✓ "Find organizations' in instructions
    
    def test_bad_task_examples_provided(self):
        """Mentalist instructions should provide examples of bad tasks"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert '✗ "Compile a comprehensive report"' in instructions
        assert '✗ "Create a summary of findings"' in instructions


class TestDebugLogging:
    """Test that debug logging is added"""
    
    def test_search_agent_logs_model_info(self):
        """Search Agent creation should log model information"""
        with patch('api.team_config.AgentFactory') as mock_agent_factory, \
             patch('api.team_config.TeamConfig.get_tools') as mock_get_tools, \
             patch('api.team_config.logger') as mock_logger:
            
            # Mock tools
            mock_tool = Mock()
            mock_tool.name = "Tavily Search"
            mock_get_tools.return_value = [mock_tool]
            
            # Mock agent
            mock_agent = Mock()
            mock_agent.id = "agent_123"
            mock_agent_factory.create.return_value = mock_agent
            
            # Create agent
            agent = TeamConfig.create_search_agent("Test Topic")
            
            # Verify logging calls
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            
            # Should log agent ID
            assert any("agent_123" in str(call) for call in log_calls)
            
            # Should log model info
            assert any("model" in str(call).lower() for call in log_calls)
            
            # Should log tools
            assert any("tool" in str(call).lower() for call in log_calls)
            
            # Should log instructions length
            assert any("instructions" in str(call).lower() for call in log_calls)
    
    def test_interaction_limit_logging_in_main(self):
        """Main.py should log interaction limit at start of execution"""
        # This is tested by checking the code exists
        # Full integration test would require running the API
        import api.main as main_module
        import inspect
        
        source = inspect.getsource(main_module.run_team_task)
        
        # Check that interaction limit is retrieved and logged
        assert "interaction_limit" in source
        assert "add_log_entry" in source
        assert "Interaction limit:" in source


class TestBackwardCompatibility:
    """Test that changes are backward compatible"""
    
    def test_search_agent_accepts_explicit_model(self):
        """Search Agent should accept explicit model_id parameter"""
        with patch('api.team_config.AgentFactory') as mock_agent_factory, \
             patch('api.team_config.TeamConfig.get_tools') as mock_get_tools:
            
            mock_tool = Mock()
            mock_get_tools.return_value = [mock_tool]
            
            mock_agent = Mock()
            mock_agent.id = "agent_123"
            mock_agent_factory.create.return_value = mock_agent
            
            # Should work with explicit model_id
            agent = TeamConfig.create_search_agent("Test Topic", model_id="custom_model_123")
            assert agent.id == "agent_123"
    
    def test_team_creation_still_works(self):
        """Team creation should still work with new changes"""
        with patch('api.team_config.TeamAgentFactory') as mock_team_factory, \
             patch('api.team_config.TeamConfig.create_search_agent') as mock_create_agent:
            
            mock_search_agent = Mock()
            mock_search_agent.id = "search_agent_123"
            mock_create_agent.return_value = mock_search_agent
            
            mock_team = Mock()
            mock_team.id = "team_123"
            mock_team_factory.create.return_value = mock_team
            
            # Should work with default parameters
            team = TeamConfig.create_team(
                topic="Test Topic",
                goals=["Goal 1"]
            )
            
            assert team.id == "team_123"


class TestInstructionsQuality:
    """Test that instructions maintain quality and completeness"""
    
    def test_search_agent_instructions_not_empty(self):
        """Search Agent instructions should not be empty"""
        instructions = get_search_agent_instructions("Test Topic")
        assert len(instructions) > 1000  # Should be substantial
    
    def test_search_agent_instructions_include_entity_types(self):
        """Search Agent instructions should still include entity type definitions"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "PERSON:" in instructions
        assert "ORGANIZATION:" in instructions
        assert "TOPIC:" in instructions
        assert "EVENT:" in instructions
        assert "POLICY:" in instructions
    
    def test_search_agent_instructions_include_output_format(self):
        """Search Agent instructions should still include output format"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "OUTPUT FORMAT:" in instructions
    
    def test_mentalist_instructions_not_empty(self):
        """Mentalist instructions should not be empty"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert len(instructions) > 2000  # Should be substantial
    
    def test_mentalist_instructions_include_mece_strategy(self):
        """Mentalist instructions should still include MECE strategy"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert "MECE DECOMPOSITION STRATEGY:" in instructions


class TestExpectedBehaviorChanges:
    """Test that expected behavior changes are reflected"""
    
    def test_search_agent_uses_gpt4o_by_default(self):
        """Search Agent should use GPT-4o to reduce timeouts"""
        # Search Agent should use GPT-4o
        assert Config.SEARCH_AGENT_MODEL == Config.GPT_4O
        assert Config.SEARCH_AGENT_MODEL == "6646261c6eb563165658bbb1"
    
    def test_instructions_address_quiz_page_issue(self):
        """Instructions should address the quiz page issue from failing run"""
        instructions = get_search_agent_instructions("Einbürgerungstests in Baden-Württemberg")
        
        # Should mention quiz detection
        assert "Wählen Sie" in instructions
        
        # Should explain what to do
        assert "skip" in instructions.lower() or "filter" in instructions.lower()
    
    def test_instructions_encourage_specific_queries(self):
        """Instructions should encourage specific queries instead of broad topics"""
        instructions = get_search_agent_instructions("Test Topic")
        
        # Should have examples of good vs bad queries
        assert "✓ Good:" in instructions or "Good:" in instructions
        assert "✗ Bad:" in instructions or "Bad:" in instructions


# Integration test markers
@pytest.mark.integration
class TestPhase1Integration:
    """Integration tests for Phase 1 changes (require API key)"""
    
    @pytest.mark.skip(reason="Requires API key and actual API call")
    def test_search_agent_with_gpt4o_completes_successfully(self):
        """Search Agent with GPT-4o should complete without timeout"""
        # This would be a real integration test
        # Skipped by default as it requires API key and costs money
        pass
    
    @pytest.mark.skip(reason="Requires API key and actual API call")
    def test_search_agent_recognizes_quiz_pages(self):
        """Search Agent should recognize and skip quiz pages"""
        # This would test with actual Tavily API
        # Skipped by default as it requires API key
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])



class TestPhase15GoogleSearchFallback:
    """Test Phase 1.5 - Google Search preference for German topics"""
    
    def test_google_search_recommended_for_german_topics(self):
        """Instructions should recommend Google Search for German topics"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "Google Search FIRST for: German government topics" in instructions
    
    def test_tavily_fallback_strategy_documented(self):
        """Instructions should document when to use Tavily as fallback"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "If Tavily times out or returns forms" in instructions
    
    def test_tool_failure_handling_documented(self):
        """Instructions should explain how to handle tool failures"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "HANDLING TOOL FAILURES:" in instructions
        assert "Agent stopped due to iteration limit" in instructions
    
    def test_german_topic_search_order_specified(self):
        """Instructions should specify search order for German topics"""
        instructions = get_search_agent_instructions("Test Topic")
        assert "FOR GERMAN GOVERNMENT TOPICS" in instructions
        assert "Start with Google Search" in instructions
    
    def test_mentalist_knows_about_google_search(self):
        """Mentalist should know Search Agent has both tools"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"]
        )
        assert "Tavily Search AND Google Search" in instructions
        assert "For German government topics: Prefer Google Search" in instructions


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])



class TestWikipediaAgentOneAtATime:
    """Test that Wikipedia Agent processes entities one at a time"""
    
    def test_wikipedia_agent_processes_one_entity(self):
        """Wikipedia Agent should process ONE entity at a time"""
        from api.instructions.wikipedia_agent import get_wikipedia_agent_instructions
        instructions = get_wikipedia_agent_instructions()
        assert "ONE entity at a time" in instructions
        assert "process exactly ONE entity" in instructions
    
    def test_wikipedia_agent_output_format_single_entity(self):
        """Wikipedia Agent output format should be for single entity"""
        from api.instructions.wikipedia_agent import get_wikipedia_agent_instructions
        instructions = get_wikipedia_agent_instructions()
        # Should NOT have "enriched_entities" array wrapper
        assert '"entity_name":' in instructions
        # Should explain single entity format
        assert "SINGLE entity" in instructions
    
    def test_mentalist_calls_wikipedia_per_entity(self):
        """Mentalist should call Wikipedia Agent once per entity"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"],
            has_wikipedia_agent=True
        )
        assert "ONE AT A TIME" in instructions
        assert "Call Wikipedia Agent separately for EACH entity" in instructions
        assert "prevents timeouts" in instructions
    
    def test_mentalist_has_wikipedia_workflow_example(self):
        """Mentalist should have example of per-entity Wikipedia workflow"""
        instructions = get_mentalist_instructions(
            topic="Test Topic",
            goals=["Test goal"],
            has_wikipedia_agent=True
        )
        assert "Example workflow:" in instructions
        assert 'Call Wikipedia Agent for "Dr. Manfred Lucha"' in instructions


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
