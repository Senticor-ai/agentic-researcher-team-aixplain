"""
Unit test to verify Task 5 enhancements to Mentalist instructions
Tests the instruction content without requiring a running API server
"""
import pytest
import sys
sys.path.insert(0, 'api')

from instructions.mentalist import get_mentalist_instructions

pytestmark = pytest.mark.unit

def test_multi_round_search_strategy():
    """Test that multi-round search strategy is present"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 1: Multi-Round Search Strategy")
    print("="*70)
    
    checks = [
        ("Round 1: Direct Search", "Round 1: Direct Search"),
        ("Round 2: Alternative Terms", "Round 2: Alternative Terms"),
        ("Round 3: Deep Dive", "Round 3: Deep Dive"),
        ("Round 4: Wikipedia Discovery", "Round 4: Wikipedia Discovery"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_feedback_loops():
    """Test that feedback loop logic is present"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 2: Feedback Loop Logic")
    print("="*70)
    
    checks = [
        ("Feedback loops section", "FEEDBACK LOOPS"),
        ("Entity count assessment", "Entity Count by Type"),
        ("Coverage quality", "Coverage Quality"),
        ("Search effectiveness", "Search Effectiveness"),
        ("Progress assessment", "Progress Assessment"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_completion_criteria():
    """Test that completion criteria are present"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 3: Completion Criteria")
    print("="*70)
    
    checks = [
        ("Continue searching criteria", "CONTINUE SEARCHING IF"),
        ("Stop criteria", "ONLY STOP WHEN"),
        ("Entity count threshold", "Total entities < 10"),
        ("Interaction budget check", "steps remaining > 5"),
        ("Search round minimum", "3 search rounds completed"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_search_term_variations():
    """Test that search term variation patterns are present"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 4: Search Term Variation Patterns")
    print("="*70)
    
    checks = [
        ("Search patterns section", "SEARCH TERM VARIATION PATTERNS"),
        ("Topic searches", "Topic Searches:"),
        ("Event searches", "Event Searches:"),
        ("Policy searches", "Policy Searches:"),
        ("People searches", "People Searches:"),
        ("Organization searches", "Organization Searches:"),
        ("Authoritative sources", "Authoritative Source Searches:"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_exhaustive_research_emphasis():
    """Test that exhaustive research emphasis is present"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 5: Exhaustive Research Emphasis")
    print("="*70)
    
    checks = [
        ("Critical emphasis", "CRITICAL: EXHAUSTIVE RESEARCH REQUIRED"),
        ("Use all steps", "USE ALL AVAILABLE STEPS"),
        ("Don't return early", "Do NOT return early"),
        ("Interaction limit mention", "typically 50 steps"),
        ("Progress tracking", "PROGRESS TRACKING AND MONITORING"),
        ("Early warning indicators", "EARLY WARNING INDICATORS"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_new_entity_types():
    """Test that new entity types are mentioned"""
    instructions = get_mentalist_instructions("Test Topic", has_wikipedia_agent=True)
    
    print("\n" + "="*70)
    print("TEST 6: New Entity Types (Topic, Event, Policy)")
    print("="*70)
    
    checks = [
        ("Topic entities", "Topic entities"),
        ("Event entities", "Event entities"),
        ("Policy entities", "Policy entities"),
        ("All 5 types listed", "Person, Organization, Topic, Event, Policy"),
    ]
    
    passed = 0
    for name, pattern in checks:
        if pattern in instructions:
            print(f"✅ {name} - Found")
            passed += 1
        else:
            print(f"❌ {name} - Missing")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TASK 5 INSTRUCTION CONTENT VERIFICATION")
    print("Testing enhanced Mentalist instructions")
    print("="*70)
    
    tests = [
        test_multi_round_search_strategy,
        test_feedback_loops,
        test_completion_criteria,
        test_search_term_variations,
        test_exhaustive_research_emphasis,
        test_new_entity_types,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 SUCCESS: All Task 5 enhancements are present in the instructions!")
        print("\nThe enhanced Mentalist instructions include:")
        print("  ✅ Multi-round search strategy (4 rounds)")
        print("  ✅ Feedback loop logic after each round")
        print("  ✅ Clear completion criteria")
        print("  ✅ Search term variation patterns")
        print("  ✅ Exhaustive research emphasis")
        print("  ✅ Support for new entity types (Topic, Event, Policy)")
        print("\nThese enhancements should lead to:")
        print("  • More comprehensive entity extraction")
        print("  • Better coverage of diverse entity types")
        print("  • More thorough use of interaction budget")
        print("  • Improved search strategies")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Some expected enhancements are missing from the instructions.")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
