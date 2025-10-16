#!/usr/bin/env python3
"""
Test script to verify Response Generator format parsing

This tests that the entity processor correctly handles the Response Generator's
JSON output format with keys like "Person", "Organization", etc.
"""
import json
import pytest
from api.entity_processor import EntityProcessor

# Simulate Response Generator output (from step 19)
response_generator_output = {
    "Person": [
        {
            "name": "Angela Pittermann",
            "job_title": "Stellvertretende Vorsitzende",
            "description": "Angela Pittermann ist die stellvertretende Vorsitzende des Familienforums Markdorf.",
            "sources": [
                "https://www.example.com/familienforum-markdorf: \"Angela Pittermann zur neuen stellvertretenden Vorsitzenden gewählt\""
            ]
        },
        {
            "name": "Eva Fast",
            "job_title": "Vorsitzende",
            "description": "Eva Fast war die Vorsitzende des Familienforums Markdorf.",
            "sources": [
                "https://www.example.com/familienforum-markdorf: \"Eva Fast gibt Amt als Vorsitzende ab\""
            ]
        },
        {
            "name": "Melanie Ganz",
            "job_title": "Vorstandsmitglied",
            "description": "Melanie Ganz ist Mitglied des Vorstands des Familienforums Markdorf.",
            "sources": [
                "https://www.example.com/familienforum-markdorf: \"Der Vorstand des Familienforums\""
            ]
        }
    ],
    "Organization": [
        {
            "name": "Familienforum Markdorf e.V.",
            "website": "https://www.mgh-markdorf.de",
            "description": "Das Familienforum Markdorf e.V. ist ein gemeinnütziger Verein.",
            "sources": [
                "https://www.mgh-markdorf.de: \"Familienforum Markdorf e.V.\""
            ]
        },
        {
            "name": "Jugendamt Bodenseekreis",
            "website": "https://www.bodenseekreis.de/jugendamt",
            "description": "Das Jugendamt Bodenseekreis fördert und begleitet den Familientreff Markdorf.",
            "sources": [
                "https://www.bodenseekreis.de/jugendamt: \"Jugendamt Bodenseekreis\""
            ]
        },
        {
            "name": "Turnverein Markdorf e.V.",
            "website": "https://www.turnverein-markdorf.de",
            "description": "Der Turnverein Markdorf e.V. ist ein Sportverein.",
            "sources": [
                "https://www.turnverein-markdorf.de: \"Turnverein Markdorf e.V.\""
            ]
        }
    ],
    "Event": [
        {
            "name": "Familienforum Markdorf 30-jähriges Jubiläum",
            "date": "2022-07-12",
            "description": "The Familienforum Markdorf celebrated its 30th anniversary.",
            "sources": [
                "https://www.example.com/familienforum-markdorf: \"Familienforum Markdorf feiert 30-jähriges Jubiläum\""
            ]
        },
        {
            "name": "SPIRITS Festival 2025",
            "date": "2025-10-14 to 2025-10-18",
            "description": "The SPIRITS Festival 2025 is a Kindertheaterfestival.",
            "sources": [
                "https://www.example.com/spirits-festival: \"SPIRITS Festival 2025\""
            ]
        }
    ],
    "Topic": [
        {
            "name": "Familienunterstützung",
            "description": "Die Unterstützung von Familien ist ein zentrales Thema.",
            "sources": [
                "https://www.mgh-markdorf.de: \"Familienforum Markdorf e.V.\"",
                "https://www.bodenseekreis.de/jugendamt: \"Jugendamt Bodenseekreis\""
            ]
        },
        {
            "name": "Mehrgenerationenhaus",
            "description": "Das Mehrgenerationenhaus in Markdorf ist ein wichtiger Treffpunkt.",
            "sources": [
                "https://www.mgh-markdorf.de: \"Mehrgenerationenhaus Markdorf\""
            ]
        }
    ]
}

@pytest.mark.unit
def test_response_generator_format():
    """Test that Response Generator format is correctly parsed"""
    print("Testing Response Generator format parsing...")
    print(f"Input has {len(response_generator_output)} entity type groups")
    
    # Count total entities in input
    total_input = sum(len(entities) for entities in response_generator_output.values())
    print(f"Total entities in input: {total_input}")
    
    # Convert using the entity processor
    result = EntityProcessor.convert_grouped_entities(response_generator_output)
    
    # Check result
    entities = result.get("entities", [])
    print(f"\nConverted to {len(entities)} entities")
    
    # Count by type
    type_counts = {}
    for entity in entities:
        entity_type = entity.get("type", "Unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
    
    print("\nEntity type breakdown:")
    for entity_type, count in sorted(type_counts.items()):
        print(f"  {entity_type}: {count}")
    
    # Verify counts match
    expected_counts = {
        "Person": 3,
        "Organization": 3,
        "Event": 2,
        "Topic": 2
    }
    
    # Verify counts match
    for entity_type, expected_count in expected_counts.items():
        actual_count = type_counts.get(entity_type, 0)
        assert actual_count == expected_count, f"Expected {expected_count} {entity_type} entities, got {actual_count}"
    
    # Verify total count
    assert len(entities) == total_input, f"Expected {total_input} entities, got {len(entities)}"
    
    print(f"\n✅ SUCCESS: All {total_input} entities correctly parsed!")

if __name__ == "__main__":
    # Run the test standalone
    try:
        test_response_generator_format()
        print("\n✅ All tests passed!")
        exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
