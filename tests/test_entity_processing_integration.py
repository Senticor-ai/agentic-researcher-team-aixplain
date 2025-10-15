"""
Integration test for entity processing with real agent output
Tests the complete flow from agent response to UI-ready JSON-LD output
"""
import pytest
import json
from api.entity_processor import EntityProcessor


# Real agent output from AWO Karlsruhe research
MOCK_AGENT_OUTPUT = {
    "Person Entities": [
        {
            "name": "Markus Barton",
            "job_title": "Geschäftsführer (Managing Director)",
            "description": "Markus Barton is the Managing Director of AWO Karlsruhe gGmbH, responsible for overseeing the organization's operations and strategic direction.",
            "sources": [
                "https://www.awo-karlsruhe.de: \"Geschäftsführung; Geschäftsführer Markus Barton Tel.: 0721 35007-121. E-Mail: m.barton@awo-karlsruhe.de\""
            ]
        },
        {
            "name": "Pascal Deceuninck",
            "job_title": "Sozial Arbeiter (Social Worker)",
            "description": "Pascal Deceuninck works as a social worker at AWO Karlsruhe gGmbH, contributing to the organization's social services and support for various community groups.",
            "sources": [
                "https://www.linkedin.com: \"Pascal Deceuninck. Sozial Arbeiter at Get Real! FAE & SPFH, AWO Karlsruhe gemeinnützige GmbH.\""
            ]
        }
    ],
    "Organization Entities": [
        {
            "name": "AWO Karlsruhe gGmbH",
            "description": "A non-profit organization focused on social welfare, offering a range of social services for all ages and life stages.",
            "sources": [
                "https://linktr.ee/awokarlsruhe: \"AWO Karlsruhe gGmbH - Soziale Dienstleistungen für alle Altersgruppen.\""
            ]
        }
    ],
    "Event Entities": [
        {
            "name": "Quartiersfest im Mühlburger Feld",
            "date": "Not specified",
            "location": "Mühlburger Feld",
            "description": "A community event organized by AWO Karlsruhe, featuring drinks, actions, snacks, and music.",
            "sources": [
                "https://linktr.ee/awokarlsruhe: \"Quartiersfest im Mühlburger Feld - Eine Veranstaltung der AWO Karlsruhe.\""
            ]
        },
        {
            "name": "WOLO-Cup 2025",
            "date": "Not specified",
            "location": "Not specified",
            "description": "An event focused on community and fair play, organized by AWO Karlsruhe.",
            "sources": [
                "https://linktr.ee/awokarlsruhe: \"WOLO-Cup 2025 - Ein Event der AWO Karlsruhe für Gemeinschaft und fairen Spiel.\""
            ]
        }
    ],
    "Topic Entities": [
        {
            "name": "Soziale Dienstleistungen",
            "description": "Social services offered by AWO Karlsruhe, including childcare, school social work, and support for children and youth.",
            "relationship": "AWO Karlsruhe gGmbH",
            "sources": [
                "https://linktr.ee/awokarlsruhe: \"Soziale Dienstleistungen - Ein Angebot der AWO Karlsruhe für alle Altersgruppen.\""
            ]
        },
        {
            "name": "Kinder- und Jugendhilfe",
            "description": "Child and youth welfare services provided by AWO Karlsruhe gGmbH, including support for children and youth in need.",
            "relationship": "AWO Karlsruhe gGmbH",
            "sources": [
                "https://www.awo-karlsruhe.de: \"Kinder- und Jugendhilfe\""
            ]
        }
    ]
}


def test_parse_agent_output_with_entity_groups():
    """Test parsing agent output that groups entities by type"""
    # Create mock agent response with output in intermediate steps
    agent_response = {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": json.dumps(MOCK_AGENT_OUTPUT)
            }
        ],
        "output": "Final report...",
        "completed": True
    }
    
    # Process the response
    entities_data = EntityProcessor.receive_entities_from_agent(agent_response)
    
    # Verify we got entities
    assert "entities" in entities_data
    entities = entities_data["entities"]
    
    # Should have entities from all types
    assert len(entities) > 0
    
    # Count by type
    person_count = sum(1 for e in entities if e.get("type") == "Person")
    org_count = sum(1 for e in entities if e.get("type") == "Organization")
    event_count = sum(1 for e in entities if e.get("type") == "Event")
    topic_count = sum(1 for e in entities if e.get("type") == "Topic")
    
    print(f"\nExtracted entities:")
    print(f"  - Persons: {person_count}")
    print(f"  - Organizations: {org_count}")
    print(f"  - Events: {event_count}")
    print(f"  - Topics: {topic_count}")
    
    # Verify we got the expected counts
    assert person_count == 2, f"Expected 2 persons, got {person_count}"
    assert org_count == 1, f"Expected 1 organization, got {org_count}"
    assert event_count == 2, f"Expected 2 events, got {event_count}"
    assert topic_count == 2, f"Expected 2 topics, got {topic_count}"


def test_full_entity_processing_pipeline():
    """Test the complete pipeline from agent response to JSON-LD sachstand"""
    # Create mock agent response
    agent_response = {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": json.dumps(MOCK_AGENT_OUTPUT)
            }
        ],
        "output": "Research completed",
        "completed": True
    }
    
    # Process through the full pipeline
    sachstand, mece_graph, validation_metrics = EntityProcessor.process_agent_response(
        agent_response=agent_response,
        topic="AWO Karlsruhe gGmbH",
        completion_status="complete"
    )
    
    # Verify sachstand structure
    assert sachstand is not None
    assert "@context" in sachstand
    assert sachstand["@context"] == "https://schema.org"
    assert sachstand["@type"] == "ResearchReport"
    assert "hasPart" in sachstand
    
    # Verify entities in hasPart
    entities = sachstand["hasPart"]
    assert len(entities) > 0
    
    # Verify entity structure
    for entity in entities:
        assert "@type" in entity
        assert "name" in entity
        assert entity["@type"] in ["Person", "Organization", "Event", "Topic"]
        
        # Verify sources
        if "citation" in entity:
            assert isinstance(entity["citation"], list)
            for citation in entity["citation"]:
                assert citation["@type"] == "WebPage"
                assert "url" in citation
    
    # Verify validation metrics
    assert validation_metrics is not None
    assert "total_entities" in validation_metrics
    assert "valid_entities" in validation_metrics
    assert validation_metrics["total_entities"] > 0
    assert validation_metrics["valid_entities"] > 0
    
    print(f"\nValidation metrics:")
    print(f"  - Total entities: {validation_metrics['total_entities']}")
    print(f"  - Valid entities: {validation_metrics['valid_entities']}")
    print(f"  - Rejected entities: {validation_metrics['rejected_entities']}")
    print(f"  - Avg quality score: {validation_metrics['avg_quality_score']:.2f}")


def test_entity_types_preserved():
    """Test that all entity types are preserved through processing"""
    agent_response = {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": json.dumps(MOCK_AGENT_OUTPUT)
            }
        ],
        "output": "Research completed",
        "completed": True
    }
    
    sachstand, _, _ = EntityProcessor.process_agent_response(
        agent_response=agent_response,
        topic="AWO Karlsruhe gGmbH",
        completion_status="complete"
    )
    
    entities = sachstand["hasPart"]
    entity_types = {e["@type"] for e in entities}
    
    # Verify all expected types are present
    assert "Person" in entity_types
    assert "Organization" in entity_types
    assert "Event" in entity_types
    assert "Topic" in entity_types
    
    print(f"\nEntity types found: {entity_types}")


def test_entity_fields_preserved():
    """Test that entity-specific fields are preserved"""
    agent_response = {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": json.dumps(MOCK_AGENT_OUTPUT)
            }
        ],
        "output": "Research completed",
        "completed": True
    }
    
    sachstand, _, _ = EntityProcessor.process_agent_response(
        agent_response=agent_response,
        topic="AWO Karlsruhe gGmbH",
        completion_status="complete"
    )
    
    entities = sachstand["hasPart"]
    
    # Find a person entity and verify jobTitle
    person = next((e for e in entities if e["@type"] == "Person"), None)
    assert person is not None
    assert "jobTitle" in person or "description" in person
    
    # Find an event entity and verify event-specific fields
    event = next((e for e in entities if e["@type"] == "Event"), None)
    assert event is not None
    # Event should have description at minimum
    assert "description" in event
    
    # Find a topic entity
    topic = next((e for e in entities if e["@type"] == "Topic"), None)
    assert topic is not None
    assert "description" in topic
    
    print(f"\nSample Person entity: {person.get('name')}")
    print(f"Sample Event entity: {event.get('name')}")
    print(f"Sample Topic entity: {topic.get('name')}")


def test_sources_converted_to_citations():
    """Test that sources are properly converted to schema.org citations"""
    agent_response = {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": json.dumps(MOCK_AGENT_OUTPUT)
            }
        ],
        "output": "Research completed",
        "completed": True
    }
    
    sachstand, _, _ = EntityProcessor.process_agent_response(
        agent_response=agent_response,
        topic="AWO Karlsruhe gGmbH",
        completion_status="complete"
    )
    
    entities = sachstand["hasPart"]
    
    # Check that entities have citations
    entities_with_citations = [e for e in entities if "citation" in e]
    assert len(entities_with_citations) > 0
    
    # Verify citation structure
    for entity in entities_with_citations:
        for citation in entity["citation"]:
            assert citation["@type"] == "WebPage"
            assert "url" in citation
            assert isinstance(citation["url"], str)
            assert citation["url"].startswith("http")
    
    print(f"\nEntities with citations: {len(entities_with_citations)}/{len(entities)}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
