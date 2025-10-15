"""
Test Enhanced Instructions - Direct Comparison

This test suite verifies the enhanced search agent instructions (Task 4)
to ensure all new features are present and prevent regression.

Run with: pytest tests/test_instructions_comparison.py -v
Run regression tests only: pytest -m regression -v
"""
import pytest
from api.instructions.search_agent import get_search_agent_instructions


@pytest.mark.regression
class TestEnhancedInstructions:
    """
    Regression test suite for Task 4: Enhanced entity extraction instructions
    
    These tests ensure that the enhanced extraction features remain intact:
    - New entity types (TOPIC, EVENT, POLICY)
    - Comprehensive examples in German and English
    - Detailed output formats with dates and identifiers
    - Complete coverage extraction strategy
    - Feedback mechanism with entity counts
    """

    def test_entity_type_definitions(self):
        """Test that all entity type definitions are present"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "**PERSON**: Individuals mentioned" in instructions, "PERSON definition missing"
        assert "**ORGANIZATION**: Institutions, companies" in instructions, "ORGANIZATION definition missing"
        assert "**TOPIC**: Themes, subjects, policy areas" in instructions, "TOPIC definition missing"
        assert "**EVENT**: Conferences, announcements" in instructions, "EVENT definition missing"
        assert "**POLICY**: Laws, regulations" in instructions, "POLICY definition missing"

    def test_examples_coverage(self):
        """Test that examples cover all entity types"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "Example 1 - German Government Official (PERSON)" in instructions, "PERSON example missing"
        assert ("Example 2 - German Ministry (ORGANIZATION)" in instructions or 
                "Example 3 - NGO (ORGANIZATION)" in instructions), "ORGANIZATION example missing"
        assert ("Example 4 - Policy Area (TOPIC)" in instructions or 
                "Example 5 - Climate Theme (TOPIC" in instructions), "TOPIC example missing"
        assert ("Example 6 - Policy Announcement (EVENT)" in instructions or 
                "Example 7 - Conference (EVENT" in instructions), "EVENT example missing"
        assert ("Example 8 - German Law (POLICY)" in instructions or 
                "Example 9 - Government Program (POLICY" in instructions), "POLICY example missing"
        assert "Kinderarmut" in instructions and "Klimaschutz" in instructions, "German examples missing"
        assert "Climate change" in instructions or "Healthcare reform" in instructions, "English examples missing"

    def test_output_formats(self):
        """Test that output formats are defined for all types"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "PERSON: [Name]" in instructions and "Job Title:" in instructions, "PERSON format incomplete"
        assert "ORGANIZATION: [Name]" in instructions and "Website:" in instructions, "ORGANIZATION format incomplete"
        assert "TOPIC: [Topic Name]" in instructions, "TOPIC format missing"
        assert "EVENT: [Event Name]" in instructions and "Date: [YYYY-MM-DD" in instructions, "EVENT format incomplete"
        assert "Location: [Location if available]" in instructions, "EVENT location field missing"
        assert "POLICY: [Policy/Law Name]" in instructions and "Identifier:" in instructions, "POLICY format incomplete"
        assert "Effective Date: [YYYY-MM-DD" in instructions, "POLICY effective date missing"
        assert "Jurisdiction: [Geographic" in instructions, "POLICY jurisdiction missing"
        assert "ISO 8601 format: YYYY-MM-DD" in instructions, "Date format guidelines missing"

    def test_extraction_strategy(self):
        """Test that comprehensive extraction strategy is present"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "Process EVERY search result systematically" in instructions, "Process ALL results missing"
        assert "Extract at MINIMUM one entity per search result" in instructions, "Minimum entity requirement missing"
        assert "extract the organization that owns/publishes it" in instructions, "Source organization extraction missing"
        assert "1.5+ entities per result" in instructions, "Entity per result goal missing"
        assert "10-20 entities total" in instructions, "Total entity goal missing"
        assert "For government websites (.gov, .de, .bund.de)" in instructions, "Government website guidance missing"
        assert "For NGO websites: Extract the NGO" in instructions, "NGO website guidance missing"
        assert "MUST extract dates/deadlines when mentioned" in instructions, "Temporal info requirement missing"
        assert "MUST extract identifiers (law numbers)" in instructions, "Policy identifier requirement missing"

    def test_feedback_mechanism(self):
        """Test that feedback mechanism is present"""
        instructions = get_search_agent_instructions("Test Topic")
        
        # Phase 1 simplified the feedback mechanism - Search Agent no longer compiles reports
        # Now uses simplified "SEARCH EFFECTIVENESS NOTES" instead of detailed "EXTRACTION SUMMARY"
        assert "SEARCH EFFECTIVENESS NOTES:" in instructions, "Search effectiveness notes section missing"
        assert "Keep notes brief" in instructions, "Brief notes instruction missing"
        
        # Still requires extraction summary with entity counts
        assert "extraction summary with entity counts by type" in instructions.lower(), "Entity count requirement missing"

    def test_instruction_length(self):
        """Test that instructions are comprehensive"""
        instructions = get_search_agent_instructions("Test Topic")
        length = len(instructions)
        
        # Should be significantly longer with all the new content
        min_expected = 10000  # At least 10k characters
        
        assert length >= min_expected, f"Instructions too short: {length} < {min_expected} characters"

    def test_german_language_support(self):
        """Test that German language examples and terms are present"""
        instructions = get_search_agent_instructions("Test Topic")
        
        # Check for German examples
        assert "Kinderarmut" in instructions, "German example 'Kinderarmut' missing"
        assert "Klimaschutz" in instructions, "German example 'Klimaschutz' missing"
        assert "Bundesteilhabegesetz" in instructions, "German policy example missing"
        
        # Check for German language guidance
        assert "German examples:" in instructions, "German examples section missing"
        assert "Baden-Württemberg" in instructions, "Baden-Württemberg references missing"

    def test_temporal_information_requirements(self):
        """Test that temporal information requirements are explicit"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "MUST extract dates/deadlines when mentioned" in instructions, "Date extraction requirement missing"
        assert "ISO 8601 format: YYYY-MM-DD" in instructions, "ISO 8601 date format missing"
        assert "Date: [YYYY-MM-DD" in instructions, "Date field format missing"
        assert "Effective Date:" in instructions, "Effective date field missing"

    def test_policy_identifier_requirements(self):
        """Test that policy identifier requirements are explicit"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "MUST extract identifiers (law numbers)" in instructions, "Identifier extraction requirement missing"
        assert "Identifier: [Official identifier" in instructions, "Identifier field format missing"
        assert "Jurisdiction:" in instructions, "Jurisdiction field missing"

    def test_complete_coverage_strategy(self):
        """Test that complete coverage strategy is emphasized"""
        instructions = get_search_agent_instructions("Test Topic")
        
        assert "CRITICAL - EXTRACT FROM ALL SEARCH RESULTS:" in instructions, "Critical coverage section missing"
        assert "do not skip any results" in instructions, "No skip instruction missing"
        assert "at least the source organization" in instructions, "Source organization minimum missing"
