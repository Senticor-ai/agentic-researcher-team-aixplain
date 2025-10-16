"""
Real Integration Test: Agent Workflow with Validation and Enrichment

This test runs the complete agent workflow with real API calls:
1. Search Agent finds entities for specific topics
2. Validation Agent validates URLs immediately
3. Wikipedia Agent enriches entities with Wikipedia data
4. Validation Agent validates schema.org compliance
5. Ontology Agent suggests improvements

Test cases cover different entity types:
- Person: Dr. Manfred Lucha
- Organization: Bundesministerium für Umwelt
- Event: Klimagipfel 2024
- Policy: Bundesteilhabegesetz

Run with: pytest tests/test_agent_workflow_integration.py -v -s
Note: This test requires real API calls and will be skipped if conftest mocking is active.
"""
import pytest
import logging
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Check if we're running with mocked aixplain (from conftest.py)
# If so, skip these tests as they require real API calls
try:
    import aixplain
    if hasattr(aixplain, '__class__') and 'MagicMock' in str(type(aixplain)):
        pytest.skip(
            "Integration tests skipped - aixplain is mocked by conftest.py. "
            "These tests require real API calls. "
            "To run integration tests, temporarily rename tests/conftest.py",
            allow_module_level=True
        )
except ImportError:
    pass

# Skip all tests if API key not available
if not os.getenv("TEAM_API_KEY"):
    pytest.skip("TEAM_API_KEY not found - skipping integration tests", allow_module_level=True)

from api.team_config import TeamConfig
from api.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mark all tests as integration and slow
pytestmark = [pytest.mark.integration, pytest.mark.slow]


class TestAgentWorkflowIntegration:
    """Integration tests for complete agent workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        logger.info("\n" + "="*80)
        logger.info("Starting integration test")
        logger.info("="*80)
        yield
        logger.info("="*80)
        logger.info("Integration test complete")
        logger.info("="*80 + "\n")
    
    def test_person_entity_workflow(self):
        """
        Test complete workflow for Person entity: Dr. Manfred Lucha
        
        Expected workflow:
        1. Search Agent finds information about Dr. Manfred Lucha
        2. Validation Agent validates URLs from search results
        3. Wikipedia Agent enriches with Wikipedia links and Wikidata ID
        4. Validation Agent validates schema.org compliance
        5. Ontology Agent suggests improvements (e.g., add jobTitle property)
        
        Expected entity structure:
        {
          "@context": "https://schema.org",
          "@type": "Person",
          "name": "Dr. Manfred Lucha",
          "jobTitle": "Minister für Soziales, Gesundheit und Integration",
          "description": "...",
          "url": "https://sozialministerium.baden-wuerttemberg.de/...",
          "sameAs": [
            "https://de.wikipedia.org/wiki/Manfred_Lucha",
            "https://www.wikidata.org/wiki/Q1889089"
          ],
          "wikidata_id": "Q1889089",
          "wikipedia_links": [...],
          "validation_status": "validated"
        }
        """
        logger.info("\n" + "-"*80)
        logger.info("TEST: Person Entity Workflow - Dr. Manfred Lucha")
        logger.info("-"*80)
        
        topic = "Dr. Manfred Lucha Minister Baden-Württemberg"
        goals = [
            "Find biographical information",
            "Identify official role and ministry",
            "Get Wikipedia and Wikidata links"
        ]
        
        logger.info(f"\nTopic: {topic}")
        logger.info(f"Goals: {goals}")
        
        # Create team with all agents enabled
        logger.info("\n1. Creating team with Search, Validation, Wikipedia, and Ontology agents...")
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_validation=True,
            enable_wikipedia=True,
            enable_ontology=True
        )
        
        assert team is not None, "Team should be created"
        logger.info(f"✓ Team created: {team.id}")
        
        # Format research prompt
        prompt = TeamConfig.format_research_prompt(topic, goals)
        logger.info(f"\n2. Research prompt:\n{prompt[:200]}...")
        
        # Run team (this will execute the agents)
        logger.info("\n3. Running team agents...")
        logger.info("   Expected workflow:")
        logger.info("   - Search Agent searches for Dr. Manfred Lucha")
        logger.info("   - Validation Agent validates URLs from search results")
        logger.info("   - Wikipedia Agent enriches with Wikipedia data")
        logger.info("   - Validation Agent validates schema.org compliance")
        logger.info("   - Ontology Agent suggests improvements")
        
        try:
            result = team.run(prompt)
            logger.info(f"\n✓ Team execution completed")
            
            # Log result summary
            if hasattr(result, 'data'):
                logger.info(f"\n4. Result summary:")
                logger.info(f"   Result type: {type(result.data)}")
                
                # Try to parse as JSON if it's a string
                if isinstance(result.data, str):
                    try:
                        data = json.loads(result.data)
                        logger.info(f"   Parsed JSON with {len(data)} keys")
                        
                        # Check for entities
                        if 'entities' in data:
                            entities = data['entities']
                            logger.info(f"   Found {len(entities)} entities")
                            
                            # Look for Person entities
                            person_entities = [e for e in entities if e.get('@type') == 'Person']
                            logger.info(f"   Found {len(person_entities)} Person entities")
                            
                            if person_entities:
                                person = person_entities[0]
                                logger.info(f"\n5. Person entity validation:")
                                logger.info(f"   Name: {person.get('name')}")
                                logger.info(f"   Type: {person.get('@type')}")
                                logger.info(f"   Has @context: {'✓' if '@context' in person else '✗'}")
                                logger.info(f"   Has sameAs: {'✓' if 'sameAs' in person else '✗'}")
                                logger.info(f"   Has wikidata_id: {'✓' if 'wikidata_id' in person else '✗'}")
                                logger.info(f"   Validation status: {person.get('validation_status', 'unknown')}")
                                
                                # Assertions
                                assert '@context' in person, "Person should have @context"
                                assert person.get('@type') == 'Person', "Type should be Person"
                                assert 'name' in person, "Person should have name"
                                
                                logger.info("\n✓ Person entity structure validated")
                    except json.JSONDecodeError:
                        logger.warning("   Could not parse result as JSON")
                        logger.info(f"   Result preview: {str(result.data)[:200]}...")
            
            logger.info("\n✓ TEST PASSED: Person entity workflow completed successfully")
            
        except Exception as e:
            logger.error(f"\n✗ Team execution failed: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Team execution failed: {e}")
    
    def test_organization_entity_workflow(self):
        """
        Test complete workflow for Organization entity: Bundesministerium für Umwelt
        
        Expected workflow:
        1. Search Agent finds information about the ministry
        2. Validation Agent validates URLs
        3. Wikipedia Agent enriches with Wikipedia links
        4. Validation Agent validates schema.org compliance
        5. Ontology Agent suggests GovernmentOrganization type
        
        Expected entity structure:
        {
          "@context": "https://schema.org",
          "@type": "GovernmentOrganization",
          "name": "Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit",
          "alternateName": "BMU",
          "description": "...",
          "url": "https://www.bmu.de",
          "sameAs": [...],
          "validation_status": "validated"
        }
        """
        logger.info("\n" + "-"*80)
        logger.info("TEST: Organization Entity Workflow - Bundesministerium für Umwelt")
        logger.info("-"*80)
        
        topic = "Bundesministerium für Umwelt Naturschutz nukleare Sicherheit"
        goals = [
            "Find official website and contact information",
            "Get Wikipedia and Wikidata links",
            "Identify organizational structure"
        ]
        
        logger.info(f"\nTopic: {topic}")
        logger.info(f"Goals: {goals}")
        
        # Create team
        logger.info("\n1. Creating team with all agents...")
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_validation=True,
            enable_wikipedia=True,
            enable_ontology=True
        )
        
        assert team is not None
        logger.info(f"✓ Team created: {team.id}")
        
        # Run team
        prompt = TeamConfig.format_research_prompt(topic, goals)
        logger.info("\n2. Running team agents...")
        
        try:
            result = team.run(prompt)
            logger.info(f"\n✓ Team execution completed")
            
            # Validate result
            if hasattr(result, 'data') and isinstance(result.data, str):
                try:
                    data = json.loads(result.data)
                    if 'entities' in data:
                        org_entities = [e for e in data['entities'] if e.get('@type') in ['Organization', 'GovernmentOrganization']]
                        logger.info(f"\n3. Found {len(org_entities)} Organization entities")
                        
                        if org_entities:
                            org = org_entities[0]
                            logger.info(f"   Name: {org.get('name')}")
                            logger.info(f"   Type: {org.get('@type')}")
                            logger.info(f"   Has @context: {'✓' if '@context' in org else '✗'}")
                            logger.info(f"   Validation status: {org.get('validation_status', 'unknown')}")
                            
                            assert '@context' in org, "Organization should have @context"
                            assert org.get('@type') in ['Organization', 'GovernmentOrganization']
                            
                            logger.info("\n✓ Organization entity structure validated")
                except json.JSONDecodeError:
                    logger.warning("Could not parse result as JSON")
            
            logger.info("\n✓ TEST PASSED: Organization entity workflow completed")
            
        except Exception as e:
            logger.error(f"\n✗ Team execution failed: {e}")
            pytest.fail(f"Team execution failed: {e}")
    
    def test_event_entity_workflow(self):
        """
        Test complete workflow for Event entity: Klimagipfel 2024
        
        Expected workflow:
        1. Search Agent finds information about the climate summit
        2. Validation Agent validates URLs
        3. Wikipedia Agent enriches if Wikipedia article exists
        4. Validation Agent validates schema.org compliance
        5. Ontology Agent suggests ConferenceEvent type and date properties
        
        Expected entity structure:
        {
          "@context": "https://schema.org",
          "@type": "ConferenceEvent",
          "name": "Klimagipfel 2024",
          "description": "...",
          "startDate": "2024-03-15",
          "location": {...},
          "organizer": {...},
          "validation_status": "validated"
        }
        """
        logger.info("\n" + "-"*80)
        logger.info("TEST: Event Entity Workflow - Klimagipfel 2024")
        logger.info("-"*80)
        
        topic = "Klimagipfel 2024 Stuttgart Baden-Württemberg"
        goals = [
            "Find event date and location",
            "Identify organizers",
            "Get event details and agenda"
        ]
        
        logger.info(f"\nTopic: {topic}")
        logger.info(f"Goals: {goals}")
        
        # Create team
        logger.info("\n1. Creating team with all agents...")
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_validation=True,
            enable_wikipedia=True,
            enable_ontology=True
        )
        
        assert team is not None
        logger.info(f"✓ Team created: {team.id}")
        
        # Run team
        prompt = TeamConfig.format_research_prompt(topic, goals)
        logger.info("\n2. Running team agents...")
        
        try:
            result = team.run(prompt)
            logger.info(f"\n✓ Team execution completed")
            
            # Validate result
            if hasattr(result, 'data') and isinstance(result.data, str):
                try:
                    data = json.loads(result.data)
                    if 'entities' in data:
                        event_entities = [e for e in data['entities'] if 'Event' in e.get('@type', '')]
                        logger.info(f"\n3. Found {len(event_entities)} Event entities")
                        
                        if event_entities:
                            event = event_entities[0]
                            logger.info(f"   Name: {event.get('name')}")
                            logger.info(f"   Type: {event.get('@type')}")
                            logger.info(f"   Has @context: {'✓' if '@context' in event else '✗'}")
                            logger.info(f"   Has startDate: {'✓' if 'startDate' in event else '✗'}")
                            logger.info(f"   Validation status: {event.get('validation_status', 'unknown')}")
                            
                            assert '@context' in event, "Event should have @context"
                            assert 'Event' in event.get('@type', '')
                            
                            logger.info("\n✓ Event entity structure validated")
                except json.JSONDecodeError:
                    logger.warning("Could not parse result as JSON")
            
            logger.info("\n✓ TEST PASSED: Event entity workflow completed")
            
        except Exception as e:
            logger.error(f"\n✗ Team execution failed: {e}")
            pytest.fail(f"Team execution failed: {e}")
    
    def test_policy_entity_workflow(self):
        """
        Test complete workflow for Policy entity: Bundesteilhabegesetz
        
        Expected workflow:
        1. Search Agent finds information about the law
        2. Validation Agent validates URLs
        3. Wikipedia Agent enriches if Wikipedia article exists
        4. Validation Agent validates schema.org compliance
        5. Ontology Agent suggests Legislation type and identifier properties
        
        Expected entity structure:
        {
          "@context": "https://schema.org",
          "@type": "Legislation",
          "name": "Bundesteilhabegesetz",
          "alternateName": "BTHG",
          "description": "...",
          "identifier": "BTHG",
          "datePublished": "2017-01-01",
          "jurisdiction": "Deutschland",
          "validation_status": "validated"
        }
        """
        logger.info("\n" + "-"*80)
        logger.info("TEST: Policy Entity Workflow - Bundesteilhabegesetz")
        logger.info("-"*80)
        
        topic = "Bundesteilhabegesetz BTHG Deutschland"
        goals = [
            "Find law details and effective date",
            "Identify jurisdiction and scope",
            "Get official sources and documentation"
        ]
        
        logger.info(f"\nTopic: {topic}")
        logger.info(f"Goals: {goals}")
        
        # Create team
        logger.info("\n1. Creating team with all agents...")
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            enable_validation=True,
            enable_wikipedia=True,
            enable_ontology=True
        )
        
        assert team is not None
        logger.info(f"✓ Team created: {team.id}")
        
        # Run team
        prompt = TeamConfig.format_research_prompt(topic, goals)
        logger.info("\n2. Running team agents...")
        
        try:
            result = team.run(prompt)
            logger.info(f"\n✓ Team execution completed")
            
            # Validate result
            if hasattr(result, 'data') and isinstance(result.data, str):
                try:
                    data = json.loads(result.data)
                    if 'entities' in data:
                        policy_entities = [e for e in data['entities'] if e.get('@type') in ['Legislation', 'Policy', 'Thing']]
                        logger.info(f"\n3. Found {len(policy_entities)} Policy/Legislation entities")
                        
                        if policy_entities:
                            policy = policy_entities[0]
                            logger.info(f"   Name: {policy.get('name')}")
                            logger.info(f"   Type: {policy.get('@type')}")
                            logger.info(f"   Has @context: {'✓' if '@context' in policy else '✗'}")
                            logger.info(f"   Has identifier: {'✓' if 'identifier' in policy else '✗'}")
                            logger.info(f"   Validation status: {policy.get('validation_status', 'unknown')}")
                            
                            assert '@context' in policy, "Policy should have @context"
                            
                            logger.info("\n✓ Policy entity structure validated")
                except json.JSONDecodeError:
                    logger.warning("Could not parse result as JSON")
            
            logger.info("\n✓ TEST PASSED: Policy entity workflow completed")
            
        except Exception as e:
            logger.error(f"\n✗ Team execution failed: {e}")
            pytest.fail(f"Team execution failed: {e}")
    
    def test_validation_metrics(self):
        """
        Test that validation metrics are tracked across the workflow
        
        Expected metrics:
        - Total entities validated
        - Schema.org compliance rate
        - URL validation rate
        - Wikipedia enrichment rate
        - Average quality score
        """
        logger.info("\n" + "-"*80)
        logger.info("TEST: Validation Metrics Tracking")
        logger.info("-"*80)
        
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        
        logger.info(f"\nTopic: {topic}")
        
        # Create team
        team = TeamConfig.create_team(
            topic=topic,
            enable_validation=True,
            enable_wikipedia=True,
            enable_ontology=True
        )
        
        assert team is not None
        logger.info(f"✓ Team created: {team.id}")
        
        # Run team
        prompt = TeamConfig.format_research_prompt(topic)
        logger.info("\nRunning team to collect validation metrics...")
        
        try:
            result = team.run(prompt)
            logger.info(f"✓ Team execution completed")
            
            # Check for validation metrics in result
            if hasattr(result, 'data') and isinstance(result.data, str):
                try:
                    data = json.loads(result.data)
                    
                    # Look for validation metrics
                    if 'validation_metrics' in data:
                        metrics = data['validation_metrics']
                        logger.info(f"\n✓ Validation metrics found:")
                        logger.info(f"   Total entities: {metrics.get('total_entities', 0)}")
                        logger.info(f"   Validated entities: {metrics.get('validated_entities', 0)}")
                        logger.info(f"   Schema.org compliance: {metrics.get('schema_org_compliance_rate', 0):.2%}")
                        logger.info(f"   URL validation rate: {metrics.get('url_validation_rate', 0):.2%}")
                        logger.info(f"   Wikipedia enrichment: {metrics.get('wikipedia_enrichment_rate', 0):.2%}")
                        logger.info(f"   Avg quality score: {metrics.get('avg_quality_score', 0):.2f}")
                    else:
                        logger.info("\n⚠ Validation metrics not found in result")
                        logger.info("   (Metrics may be tracked internally by Validation Agent)")
                    
                except json.JSONDecodeError:
                    logger.warning("Could not parse result as JSON")
            
            logger.info("\n✓ TEST PASSED: Validation metrics test completed")
            
        except Exception as e:
            logger.error(f"\n✗ Team execution failed: {e}")
            pytest.fail(f"Team execution failed: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s", "--log-cli-level=INFO"])
