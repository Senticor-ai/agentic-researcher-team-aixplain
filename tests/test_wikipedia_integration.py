"""
Test Wikipedia integration for entity enrichment

This test verifies that:
1. Wikipedia agent is created when enabled
2. Entities are enriched with Wikipedia links
3. Wikidata IDs are captured correctly
4. Multi-language Wikipedia articles are linked
"""
import pytest
import logging
from api.team_config import TeamConfig
from api.entity_processor import EntityProcessor

pytestmark = pytest.mark.integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestWikipediaIntegration:
    """Test Wikipedia integration"""
    
    def test_wikipedia_agent_creation(self):
        """Test that Wikipedia agent can be created"""
        # Note: This will only work if Wikipedia tool ID is configured
        from api.config import Config
        wikipedia_agent = TeamConfig.create_wikipedia_agent()
        
        if Config.TOOL_IDS.get("wikipedia") is None:
            # Wikipedia tool not configured - agent should be None
            assert wikipedia_agent is None
            logger.info("Wikipedia tool not configured - skipping agent creation test")
        else:
            # Wikipedia tool configured - agent should be created
            assert wikipedia_agent is not None
            assert wikipedia_agent.name == "Wikipedia Agent"
            logger.info(f"Wikipedia agent created successfully: {wikipedia_agent.id}")
    
    def test_team_with_wikipedia_agent(self):
        """Test that team can be created with Wikipedia agent"""
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        goals = ["Find biographical information", "Identify official roles"]
        
        # Create team with Wikipedia agent enabled
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_wikipedia=True
        )
        
        assert team is not None
        assert team.name.startswith("OSINT Team")
        logger.info(f"Team created with Wikipedia agent: {team.id}")
    
    def test_team_without_wikipedia_agent(self):
        """Test that team can be created without Wikipedia agent"""
        topic = "Test topic"
        goals = ["Test goal"]
        
        # Create team with Wikipedia agent disabled
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_wikipedia=False
        )
        
        assert team is not None
        logger.info(f"Team created without Wikipedia agent: {team.id}")
    
    def test_wikipedia_data_extraction(self):
        """Test extraction of Wikipedia enrichment data from agent response"""
        # Mock agent response with Wikipedia Agent output
        mock_response = {
            "data": {
                "intermediate_steps": [
                    {
                        "agent": "Search Agent",
                        "output": {
                            "entities": [
                                {
                                    "type": "Person",
                                    "name": "Dr. Manfred Lucha",
                                    "description": "Minister",
                                    "sources": [{"url": "https://example.com", "excerpt": "test"}]
                                }
                            ]
                        }
                    },
                    {
                        "agent": "Wikipedia Agent",
                        "output": {
                            "enriched_entities": [
                                {
                                    "entity_name": "Dr. Manfred Lucha",
                                    "entity_type": "Person",
                                    "wikipedia_links": [
                                        {
                                            "language": "de",
                                            "url": "https://de.wikipedia.org/wiki/Manfred_Lucha",
                                            "title": "Manfred Lucha"
                                        },
                                        {
                                            "language": "en",
                                            "url": "https://en.wikipedia.org/wiki/Manfred_Lucha",
                                            "title": "Manfred Lucha"
                                        }
                                    ],
                                    "wikidata_id": "Q1889089",
                                    "sameAs": [
                                        "https://de.wikipedia.org/wiki/Manfred_Lucha",
                                        "https://en.wikipedia.org/wiki/Manfred_Lucha",
                                        "https://www.wikidata.org/wiki/Q1889089"
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        # Extract Wikipedia data
        wikipedia_data = EntityProcessor.extract_wikipedia_enrichment(mock_response)
        
        assert "Dr. Manfred Lucha" in wikipedia_data
        assert wikipedia_data["Dr. Manfred Lucha"]["wikidata_id"] == "Q1889089"
        assert len(wikipedia_data["Dr. Manfred Lucha"]["wikipedia_links"]) == 2
        assert len(wikipedia_data["Dr. Manfred Lucha"]["sameAs"]) == 3
        
        logger.info("Wikipedia data extraction successful")
    
    def test_wikipedia_data_merge(self):
        """Test merging Wikipedia data into entities"""
        entities_data = {
            "entities": [
                {
                    "type": "Person",
                    "name": "Dr. Manfred Lucha",
                    "description": "Minister",
                    "sources": [{"url": "https://example.com", "excerpt": "test"}]
                }
            ]
        }
        
        wikipedia_data = {
            "Dr. Manfred Lucha": {
                "wikipedia_links": [
                    {
                        "language": "de",
                        "url": "https://de.wikipedia.org/wiki/Manfred_Lucha",
                        "title": "Manfred Lucha"
                    }
                ],
                "wikidata_id": "Q1889089",
                "sameAs": [
                    "https://de.wikipedia.org/wiki/Manfred_Lucha",
                    "https://www.wikidata.org/wiki/Q1889089"
                ]
            }
        }
        
        # Merge Wikipedia data
        merged = EntityProcessor.merge_wikipedia_data(entities_data, wikipedia_data)
        
        assert merged["entities"][0]["wikidata_id"] == "Q1889089"
        assert "sameAs" in merged["entities"][0]
        assert len(merged["entities"][0]["sameAs"]) == 2
        
        logger.info("Wikipedia data merge successful")
    
    def test_jsonld_with_wikipedia_data(self):
        """Test JSON-LD generation with Wikipedia enrichment"""
        entities = [
            {
                "type": "Person",
                "name": "Dr. Manfred Lucha",
                "description": "Minister für Soziales, Gesundheit und Integration",
                "jobTitle": "Minister",
                "sources": [{"url": "https://example.com", "excerpt": "test"}],
                "sameAs": [
                    "https://de.wikipedia.org/wiki/Manfred_Lucha",
                    "https://www.wikidata.org/wiki/Q1889089"
                ],
                "wikidata_id": "Q1889089"
            }
        ]
        
        # Generate JSON-LD
        sachstand = EntityProcessor.generate_jsonld_sachstand(
            topic="Dr. Manfred Lucha",
            entities=entities,
            completion_status="complete"
        )
        
        # Verify JSON-LD structure
        assert sachstand["@context"] == "https://schema.org"
        assert sachstand["@type"] == "ResearchReport"
        assert len(sachstand["hasPart"]) == 1
        
        # Verify Wikipedia enrichment in JSON-LD
        entity = sachstand["hasPart"][0]
        assert entity["@type"] == "Person"
        assert entity["name"] == "Dr. Manfred Lucha"
        assert "sameAs" in entity
        assert len(entity["sameAs"]) == 2
        assert "identifier" in entity
        assert entity["identifier"]["propertyID"] == "Wikidata"
        assert entity["identifier"]["value"] == "Q1889089"
        
        logger.info("JSON-LD with Wikipedia data generated successfully")
    
    @pytest.mark.skip(reason="Requires Wikipedia tool ID configuration and API access")
    def test_end_to_end_wikipedia_enrichment(self):
        """
        End-to-end test with real Wikipedia agent
        
        This test requires:
        1. Wikipedia tool ID configured in team_config.py
        2. Valid aixplain API key
        3. Network access to aixplain API
        
        To run this test:
        1. Configure Wikipedia tool ID in api/team_config.py
        2. Run: pytest tests/test_wikipedia_integration.py::TestWikipediaIntegration::test_end_to_end_wikipedia_enrichment -v
        """
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        goals = ["Find biographical information and official roles"]
        
        # Create team with Wikipedia agent
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_wikipedia=True
        )
        
        # Format research prompt
        prompt = TeamConfig.format_research_prompt(topic, goals)
        
        # Run team (this will take time)
        logger.info("Running team agent with Wikipedia enrichment...")
        response = team.run(prompt)
        
        # Process response
        sachstand = EntityProcessor.process_agent_response(
            agent_response=response,
            topic=topic,
            completion_status="complete"
        )
        
        # Verify entities were extracted
        assert len(sachstand["hasPart"]) > 0
        logger.info(f"Extracted {len(sachstand['hasPart'])} entities")
        
        # Check if any entities have Wikipedia enrichment
        entities_with_wikipedia = [
            e for e in sachstand["hasPart"]
            if "sameAs" in e or "identifier" in e
        ]
        
        if entities_with_wikipedia:
            logger.info(f"{len(entities_with_wikipedia)} entities enriched with Wikipedia data")
            
            # Verify Wikipedia data structure
            for entity in entities_with_wikipedia:
                if "sameAs" in entity:
                    assert isinstance(entity["sameAs"], list)
                    assert len(entity["sameAs"]) > 0
                    logger.info(f"Entity '{entity['name']}' has {len(entity['sameAs'])} sameAs links")
                
                if "identifier" in entity:
                    assert entity["identifier"]["propertyID"] == "Wikidata"
                    assert entity["identifier"]["value"].startswith("Q")
                    logger.info(f"Entity '{entity['name']}' has Wikidata ID: {entity['identifier']['value']}")
        else:
            logger.warning("No entities were enriched with Wikipedia data")
            logger.warning("This could be because:")
            logger.warning("  - Wikipedia agent was not invoked by Mentalist")
            logger.warning("  - Entities don't have Wikipedia articles")
            logger.warning("  - Wikipedia tool is not working correctly")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
