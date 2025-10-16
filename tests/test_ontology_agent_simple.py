"""
Simple Test for Ontology Agent Instructions

This test verifies the Ontology Agent instructions without requiring API credentials.
"""
from api.instructions.ontology_agent import get_ontology_agent_instructions


def test_ontology_agent_instructions():
    """Test that Ontology Agent instructions are generated correctly"""
    print("\n" + "=" * 70)
    print("  TESTING ONTOLOGY AGENT INSTRUCTIONS")
    print("=" * 70)
    
    instructions = get_ontology_agent_instructions()
    
    # Test 1: Instructions are not empty
    assert len(instructions) > 0, "Instructions should not be empty"
    print("\n✓ Test 1: Instructions generated (length: {} characters)".format(len(instructions)))
    
    # Test 2: Contains key sections
    key_sections = [
        "Ontology Agent",
        "schema.org",
        "AUTONOMOUS BEHAVIOR",
        "SUGGESTION FORMAT",
        "TYPE IMPROVEMENT",
        "RELATIONSHIP SUGGESTION"
    ]
    
    missing_sections = []
    for section in key_sections:
        if section not in instructions:
            missing_sections.append(section)
    
    assert len(missing_sections) == 0, f"Missing sections: {missing_sections}"
    print("✓ Test 2: All key sections present")
    
    # Test 3: Contains schema.org types
    schema_types = [
        "GovernmentOrganization",
        "Organization",
        "Person",
        "Event"
    ]
    
    found_types = [t for t in schema_types if t in instructions]
    assert len(found_types) >= 3, f"Expected at least 3 schema.org types, found: {found_types}"
    print(f"✓ Test 3: Schema.org types present: {', '.join(found_types)}")
    
    # Test 4: Contains relationship properties
    relationship_props = [
        "worksFor",
        "parentOrganization",
        "memberOf",
        "organizer",
        "alumniOf"
    ]
    
    found_props = [p for p in relationship_props if p in instructions]
    assert len(found_props) >= 3, f"Expected at least 3 relationship properties, found: {found_props}"
    print(f"✓ Test 4: Relationship properties present: {', '.join(found_props)}")
    
    # Test 5: Contains suggestion format examples
    format_keywords = [
        "Entity:",
        "Current Type:",
        "Suggested Type:",
        "Reason:",
        "Schema.org Reference:"
    ]
    
    found_keywords = [k for k in format_keywords if k in instructions]
    assert len(found_keywords) >= 4, f"Expected at least 4 format keywords, found: {found_keywords}"
    print(f"✓ Test 5: Suggestion format keywords present: {len(found_keywords)}/{len(format_keywords)}")
    
    # Test 6: Contains autonomous behavior description
    autonomous_keywords = [
        "autonomous",
        "monitor",
        "scan",
        "continuously"
    ]
    
    found_autonomous = [k for k in autonomous_keywords if k.lower() in instructions.lower()]
    assert len(found_autonomous) >= 2, f"Expected autonomous behavior keywords, found: {found_autonomous}"
    print(f"✓ Test 6: Autonomous behavior described")
    
    # Test 7: Contains validation integration
    assert "Validation Agent" in instructions, "Should mention Validation Agent integration"
    print("✓ Test 7: Validation Agent integration mentioned")
    
    # Test 8: Contains quality guidelines
    quality_keywords = [
        "quality",
        "semantic",
        "machine-readable",
        "value"
    ]
    
    found_quality = [k for k in quality_keywords if k.lower() in instructions.lower()]
    assert len(found_quality) >= 3, f"Expected quality guidelines, found: {found_quality}"
    print(f"✓ Test 8: Quality guidelines present")
    
    # Test 9: Contains example entities
    example_entities = [
        "Bundesministerium",
        "Ministry",
        "Minister"
    ]
    
    found_examples = [e for e in example_entities if e in instructions]
    assert len(found_examples) >= 1, f"Expected example entities, found: {found_examples}"
    print(f"✓ Test 9: Example entities present: {', '.join(found_examples)}")
    
    # Test 10: Contains schema.org references
    assert "https://schema.org/" in instructions, "Should contain schema.org URL references"
    print("✓ Test 10: Schema.org URL references present")
    
    print("\n" + "=" * 70)
    print("  ALL TESTS PASSED!")
    print("=" * 70)
    print("\n📋 Summary:")
    print(f"  • Instructions length: {len(instructions)} characters")
    print(f"  • Schema.org types: {len(found_types)}")
    print(f"  • Relationship properties: {len(found_props)}")
    print(f"  • Format keywords: {len(found_keywords)}")
    print(f"  • Example entities: {len(found_examples)}")
    print("\n✓ Ontology Agent instructions are complete and well-structured")
    
    return True


if __name__ == "__main__":
    try:
        test_ontology_agent_instructions()
        print("\n✅ SUCCESS: Ontology Agent instructions test passed!\n")
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        exit(1)
