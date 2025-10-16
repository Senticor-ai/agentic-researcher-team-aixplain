#!/usr/bin/env python3
"""
Integration test for Response Generator output format parsing

This test verifies that the entity processor correctly handles the Response Generator's
JSON output format and generates proper JSON-LD Sachstand.

Uses real sample data from tests/data/output-test-sample.json
"""
import json
import logging
from pathlib import Path

import pytest

from api.entity_processor import EntityProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sample_data():
    """Load the sample output data"""
    sample_path = Path(__file__).parent / "data" / "output-test-sample.json"
    with open(sample_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.mark.unit
def test_convert_grouped_entities():
    """Test that Response Generator format is correctly converted to standard format"""
    # Load sample data
    sample_data = load_sample_data()
    
    # Count total entities in input
    total_input = sum(len(entities) for entities in sample_data.values())
    
    # Convert using the entity processor
    result = EntityProcessor.convert_grouped_entities(sample_data)
    
    # Check result
    entities = result.get("entities", [])
    
    # Count by type
    type_counts = {}
    for entity in entities:
        entity_type = entity.get("type", "Unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    # Verify counts match
    expected_counts = {
        "Person": 3,
        "Organization": 3,
        "Event": 2,
        "Topic": 2
    }
    
    for entity_type, expected_count in expected_counts.items():
        actual_count = type_counts.get(entity_type, 0)
        assert actual_count == expected_count, f"Expected {expected_count} {entity_type} entities, got {actual_count}"
    
    assert len(entities) == total_input, f"Expected {total_input} entities, got {len(entities)}"


@pytest.mark.unit
def test_generate_jsonld_sachstand():
    """Test that JSON-LD Sachstand is correctly generated from converted entities"""
    # Load and convert sample data
    sample_data = load_sample_data()
    result = EntityProcessor.convert_grouped_entities(sample_data)
    entities = result.get("entities", [])
    
    topic = "Familienforum Markdorf"
    
    # Generate JSON-LD Sachstand
    sachstand = EntityProcessor.generate_jsonld_sachstand(
        topic=topic,
        entities=entities,
        completion_status="complete",
        mece_graph=None
    )
    
    # Validate structure
    required_fields = ["@context", "@type", "name", "dateCreated", "author", "about", "hasPart", "completionStatus"]
    for field in required_fields:
        assert field in sachstand, f"Missing required field: {field}"
    
    # Check entity count in hasPart
    has_part = sachstand.get("hasPart", [])
    
    # Verify entity types in JSON-LD
    jsonld_type_counts = {}
    for entity in has_part:
        entity_type = entity.get("@type", "Unknown")
        jsonld_type_counts[entity_type] = jsonld_type_counts.get(entity_type, 0) + 1
    
    # Verify expected counts
    expected_jsonld_counts = {
        "Person": 3,
        "Organization": 3,
        "Event": 2,
        "Topic": 2  # Topics stay as Topic in JSON-LD
    }
    
    for entity_type, expected_count in expected_jsonld_counts.items():
        actual_count = jsonld_type_counts.get(entity_type, 0)
        assert actual_count == expected_count, f"Expected {expected_count} {entity_type} entities, got {actual_count}"
    
    assert len(has_part) == 10, f"Expected 10 entities in hasPart, got {len(has_part)}"
    
    # Check that entities have proper structure
    for entity in has_part:
        assert "@type" in entity, "Entity missing @type"
        assert "name" in entity, "Entity missing name"
        assert "citation" in entity, "Entity missing citation"


@pytest.mark.unit
def test_full_pipeline():
    """Test the full pipeline from Response Generator output to JSON-LD Sachstand"""
    # Load sample data
    sample_data = load_sample_data()
    
    # Simulate agent response with Response Generator output
    mock_agent_response = {
        "data": {
            "intermediate_steps": [
                {
                    "step_number": 19,
                    "agent_name": "response_generator",
                    "agent_type": "response",
                    "output": sample_data  # Response Generator returns the grouped format
                }
            ]
        },
        "output": sample_data  # Also at root level
    }
    
    # Process the agent response
    sachstand, mece_graph, validation_metrics = EntityProcessor.process_agent_response(
        agent_response=mock_agent_response,
        topic="Familienforum Markdorf",
        completion_status="complete"
    )
    
    # Check sachstand
    has_part = sachstand.get("hasPart", [])
    
    # Note: The validator rejects entities with example.com URLs (placeholders)
    # In this test data, 5 entities have example.com URLs and are rejected
    # The 5 valid entities are: 3 Organizations + 2 Topics (with real URLs)
    expected_valid = 5  # After validation filtering
    
    # Verify entity count matches validation
    assert len(has_part) == expected_valid, f"Expected {expected_valid} valid entities, got {len(has_part)}"
    assert validation_metrics.get('valid_entities') == expected_valid, f"Expected {expected_valid} valid entities in metrics"
    assert validation_metrics.get('total_entities') == 10, "Expected 10 total entities"
    assert validation_metrics.get('rejected_entities') == 5, "Expected 5 rejected entities"


@pytest.mark.unit
def test_entity_details():
    """Test that entity details are correctly preserved"""
    # Load sample data
    sample_data = load_sample_data()
    
    # Convert to standard format
    result = EntityProcessor.convert_grouped_entities(sample_data)
    entities = result.get("entities", [])
    
    # Check Person entity details
    person_entities = [e for e in entities if e.get("type") == "Person"]
    angela = next((e for e in person_entities if e.get("name") == "Angela Pittermann"), None)
    
    assert angela is not None, "Angela Pittermann not found"
    assert angela.get('jobTitle') == "Stellvertretende Vorsitzende", f"Job title incorrect: {angela.get('jobTitle')}"
    assert len(angela.get('sources', [])) > 0, "Angela should have sources"
    
    # Check Organization entity details
    org_entities = [e for e in entities if e.get("type") == "Organization"]
    familienforum = next((e for e in org_entities if "Familienforum" in e.get("name", "")), None)
    
    assert familienforum is not None, "Familienforum Markdorf not found"
    assert familienforum.get('url') == "https://www.mgh-markdorf.de", f"URL incorrect: {familienforum.get('url')}"
    
    # Check Event entity details
    event_entities = [e for e in entities if e.get("type") == "Event"]
    spirits = next((e for e in event_entities if "SPIRITS" in e.get("name", "")), None)
    
    assert spirits is not None, "SPIRITS Festival not found"
    assert spirits.get('startDate') == "2025-10-14 to 2025-10-18", f"Date incorrect: {spirits.get('startDate')}"


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
