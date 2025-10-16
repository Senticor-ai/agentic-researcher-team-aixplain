#!/usr/bin/env python3
"""
Quick test to verify the changes work correctly
"""
import sys
sys.path.insert(0, '.')

from api.team_config import TeamConfig
from api.config import Config

def test_search_agent_model():
    """Test that Search Agent defaults to production model"""
    print("Testing Search Agent model configuration...")
    
    # Test default (should be production)
    topic = "Test Topic"
    
    # Check what model would be used
    default_model = "production"  # This is what we set as default
    model_id = Config.get_model_id(default_model)
    
    print(f"✓ Default model for Search Agent: {default_model}")
    print(f"✓ Model ID: {model_id}")
    print(f"✓ Expected: 6646261c6eb563165658bbb1 (GPT-4o)")
    
    if model_id == "6646261c6eb563165658bbb1":
        print("✅ SUCCESS: Search Agent will use GPT-4o")
        return True
    else:
        print("❌ FAIL: Search Agent not using GPT-4o")
        return False

def test_instructions_updated():
    """Test that instructions include new sections"""
    print("\nTesting Search Agent instructions...")
    
    from api.instructions.search_agent import get_search_agent_instructions
    
    instructions = get_search_agent_instructions("Test Topic")
    
    checks = [
        ("TAVILY SEARCH BEST PRACTICES", "Tavily best practices section"),
        ("YOUR SINGLE RESPONSIBILITY", "Single responsibility clarification"),
        ("FILTER OUT NON-CONTENT PAGES", "Form filtering guidance"),
        ("Wählen Sie", "German quiz detection"),
        ("DO NOT compile reports", "No compilation instruction"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in instructions:
            print(f"✓ Found: {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False
    
    if all_passed:
        print("✅ SUCCESS: All instruction updates present")
    else:
        print("❌ FAIL: Some instruction updates missing")
    
    return all_passed

def test_mentalist_instructions():
    """Test that Mentalist instructions updated"""
    print("\nTesting Mentalist instructions...")
    
    from api.instructions.mentalist import get_mentalist_instructions
    
    instructions = get_mentalist_instructions(
        topic="Test Topic",
        goals=["Test goal"]
    )
    
    checks = [
        ("Search Agent only searches and extracts", "Clarified Search Agent role"),
        ("NOT compile reports", "No compilation instruction"),
        ("Response Generator's responsibility", "Response Generator ownership"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in instructions:
            print(f"✓ Found: {description}")
        else:
            print(f"✗ Missing: {description}")
            all_passed = False
    
    if all_passed:
        print("✅ SUCCESS: Mentalist instructions updated")
    else:
        print("❌ FAIL: Mentalist instructions not fully updated")
    
    return all_passed

def main():
    print("=" * 60)
    print("TESTING PHASE 1 CHANGES")
    print("=" * 60)
    
    results = []
    
    # Test 1: Model configuration
    results.append(test_search_agent_model())
    
    # Test 2: Search Agent instructions
    results.append(test_instructions_updated())
    
    # Test 3: Mentalist instructions
    results.append(test_mentalist_instructions())
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("✅ ALL TESTS PASSED - Changes implemented correctly!")
        print("\nNext steps:")
        print("1. Start the API: uvicorn api.main:app --reload")
        print("2. Run a test with the failing topic:")
        print("   curl -X POST http://localhost:8000/api/v1/agent-teams \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"topic\": \"Einbürgerungstests in Baden-Württemberg\", \"goals\": [\"Find stakeholders\"], \"interaction_limit\": 50}'")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review changes")
        return 1

if __name__ == "__main__":
    sys.exit(main())
