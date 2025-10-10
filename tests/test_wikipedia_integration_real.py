"""
Real integration test for Wikipedia tool (no mocks)

This test uses the actual Wikipedia tool from aixplain.
Run with: poetry run pytest tests/test_wikipedia_integration_real.py -v -s
"""
import pytest
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Verify API key is loaded
if not os.getenv("TEAM_API_KEY"):
    pytest.skip("TEAM_API_KEY not found in environment", allow_module_level=True)

from api.team_config import TeamConfig
from api.entity_processor import EntityProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestWikipediaIntegrationReal:
    """Real integration tests with actual Wikipedia tool"""
    
    def test_wikipedia_tool_configured(self):
        """Test that Wikipedia tool ID is configured"""
        wikipedia_tool_id = TeamConfig.TOOL_IDS.get("wikipedia")
        
        assert wikipedia_tool_id is not None, "Wikipedia tool ID not configured"
        assert wikipedia_tool_id == "6633fd59821ee31dd914e232", "Wikipedia tool ID mismatch"
        
        logger.info(f"✓ Wikipedia tool ID configured: {wikipedia_tool_id}")
    
    def test_wikipedia_agent_creation(self):
        """Test that Wikipedia agent can be created with real tool"""
        wikipedia_agent = TeamConfig.create_wikipedia_agent(model="testing")
        
        assert wikipedia_agent is not None, "Wikipedia agent should be created"
        assert wikipedia_agent.name == "Wikipedia Agent"
        assert wikipedia_agent.id is not None
        
        logger.info(f"✓ Wikipedia agent created: {wikipedia_agent.name}")
        logger.info(f"  Agent ID: {wikipedia_agent.id}")
    
    def test_team_with_wikipedia_agent(self):
        """Test that team can be created with Wikipedia agent"""
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        goals = ["Find biographical information"]
        
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            model="testing",
            enable_wikipedia=True
        )
        
        assert team is not None
        assert team.name.startswith("OSINT Team")
        
        logger.info(f"✓ Team created with Wikipedia agent: {team.name}")
        logger.info(f"  Team ID: {team.id}")
    
    def test_wikipedia_tool_access(self):
        """Test that Wikipedia tool can be retrieved and has correct properties"""
        from aixplain.factories import ToolFactory
        
        wikipedia_tool = ToolFactory.get("6633fd59821ee31dd914e232")
        
        assert wikipedia_tool is not None
        assert wikipedia_tool.id == "6633fd59821ee31dd914e232"
        assert wikipedia_tool.name == "Wikipedia"
        
        logger.info(f"✓ Wikipedia tool retrieved: {wikipedia_tool.name}")
        logger.info(f"  Tool ID: {wikipedia_tool.id}")
    
    @pytest.mark.slow
    def test_wikipedia_tool_search(self):
        """Test Wikipedia tool search functionality"""
        from aixplain.factories import ToolFactory
        
        wikipedia_tool = ToolFactory.get("6633fd59821ee31dd914e232")
        
        # Test search for a known entity
        search_query = "Manfred Lucha"
        logger.info(f"Searching Wikipedia for: {search_query}")
        
        try:
            result = wikipedia_tool.run({"text": search_query})
            
            logger.info(f"Wikipedia search result type: {type(result)}")
            logger.info(f"Wikipedia search result: {result}")
            
            # Verify we got some result
            assert result is not None
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            pytest.fail(f"Wikipedia tool search failed: {e}")
    
    @pytest.mark.slow
    @pytest.mark.skip(reason="End-to-end test takes time - run manually when needed")
    def test_end_to_end_with_wikipedia(self):
        """
        Full end-to-end test with Wikipedia enrichment
        
        This test:
        1. Creates a team with Wikipedia agent
        2. Runs research on a known entity
        3. Verifies Wikipedia enrichment in output
        
        Run manually with:
        poetry run pytest tests/test_wikipedia_integration_real.py::TestWikipediaIntegrationReal::test_end_to_end_with_wikipedia -v -s
        """
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        goals = ["Find biographical information and official roles"]
        
        logger.info(f"Creating team for topic: {topic}")
        
        # Create team with Wikipedia agent
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            model="testing",
            enable_wikipedia=True
        )
        
        assert team is not None
        logger.info(f"✓ Team created: {team.id}")
        
        # Format research prompt
        prompt = TeamConfig.format_research_prompt(topic, goals)
        logger.info(f"Research prompt: {prompt[:200]}...")
        
        # Run team (this will take time)
        logger.info("Running team agent with Wikipedia enrichment...")
        logger.info("This may take 1-2 minutes...")
        
        response = team.run(prompt)
        
        logger.info("Team execution completed")
        logger.info(f"Response keys: {response.keys() if isinstance(response, dict) else 'not a dict'}")
        
        # Process response
        sachstand = EntityProcessor.process_agent_response(
            agent_response=response,
            topic=topic,
            completion_status="complete"
        )
        
        # Verify entities were extracted
        assert len(sachstand["hasPart"]) > 0, "No entities extracted"
        logger.info(f"✓ Extracted {len(sachstand['hasPart'])} entities")
        
        # Check for Wikipedia enrichment
        entities_with_wikipedia = [
            e for e in sachstand["hasPart"]
            if "sameAs" in e or "identifier" in e
        ]
        
        if entities_with_wikipedia:
            logger.info(f"✓ {len(entities_with_wikipedia)} entities enriched with Wikipedia data")
            
            for entity in entities_with_wikipedia:
                logger.info(f"\nEntity: {entity['name']}")
                
                if "sameAs" in entity:
                    logger.info(f"  sameAs links: {len(entity['sameAs'])}")
                    for url in entity["sameAs"]:
                        logger.info(f"    - {url}")
                
                if "identifier" in entity:
                    logger.info(f"  Wikidata ID: {entity['identifier']['value']}")
        else:
            logger.warning("⚠ No entities were enriched with Wikipedia data")
            logger.warning("This could mean:")
            logger.warning("  - Mentalist didn't invoke Wikipedia agent")
            logger.warning("  - Entities don't have Wikipedia articles")
            logger.warning("  - Wikipedia tool returned no results")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
