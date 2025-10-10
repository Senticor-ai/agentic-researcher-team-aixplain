"""
Unit tests for search strategy module

Tests the search strategy logic without requiring API server.
Run with: python tests/test_search_strategy_unit.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.search_strategy import (
    analyze_topic,
    generate_alternative_terms,
    generate_feedback,
    enhance_instructions
)


def test_analyze_topic():
    """Test topic analysis"""
    print("\n" + "=" * 80)
    print("TEST: Topic Analysis")
    print("=" * 80)
    
    test_cases = [
        {
            "topic": "Jugendschutz Baden-Württemberg 2025",
            "expected": {
                "language": "de",
                "specificity": "very_specific",
                "domain": ["government", "social"],  # Could be either
                "has_year": True,
                "has_location": True
            }
        },
        {
            "topic": "Paris France",
            "expected": {
                "language": ["en", "mixed"],  # "France" might trigger mixed
                "specificity": "broad",
                "domain": "general",
                "has_year": False,
                "has_location": False
            }
        },
        {
            "topic": "Jugendarmut Baden-Württemberg",
            "expected": {
                "language": "de",
                "specificity": ["broad", "medium"],  # 3 words could be either
                "domain": "social",
                "has_year": False,
                "has_location": True
            }
        }
    ]
    
    passed = 0
    for test in test_cases:
        topic = test["topic"]
        expected = test["expected"]
        result = analyze_topic(topic)
        
        print(f"\nTopic: {topic}")
        print(f"  Language: {result['language']} (expected: {expected['language']})")
        print(f"  Specificity: {result['specificity']} (expected: {expected['specificity']})")
        print(f"  Domain: {result['domain']} (expected: {expected['domain']})")
        print(f"  Has Year: {result['has_year']} (expected: {expected['has_year']})")
        print(f"  Has Location: {result['has_location']} (expected: {expected['has_location']})")
        
        # Check if all match (handle both single values and lists of acceptable values)
        def matches_expected(actual, expected_val):
            if isinstance(expected_val, list):
                return actual in expected_val
            return actual == expected_val
        
        matches = all(matches_expected(result[k], expected[k]) for k in expected.keys())
        if matches:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ✗ FAIL")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_generate_alternatives():
    """Test alternative term generation"""
    print("\n" + "=" * 80)
    print("TEST: Alternative Term Generation")
    print("=" * 80)
    
    test_cases = [
        {
            "topic": "Jugendschutz Baden-Württemberg 2025",
            "min_alternatives": 2,
            "should_contain": ["Jugendschutz Baden-Württemberg"]  # Without year
        },
        {
            "topic": "Sozialer Lagebericht Baden-Württemberg",
            "min_alternatives": 1,
            "should_contain": []  # Just check we get some
        },
        {
            "topic": "Paris",
            "min_alternatives": 1,
            "should_contain": []  # Broad topic should get context added
        }
    ]
    
    passed = 0
    for test in test_cases:
        topic = test["topic"]
        alternatives = generate_alternative_terms(topic)
        
        print(f"\nTopic: {topic}")
        print(f"  Alternatives generated: {len(alternatives)}")
        for i, alt in enumerate(alternatives, 1):
            print(f"    {i}. {alt}")
        
        # Check minimum count
        has_min = len(alternatives) >= test["min_alternatives"]
        
        # Check if expected terms are present
        has_expected = all(exp in alternatives for exp in test["should_contain"])
        
        if has_min and (not test["should_contain"] or has_expected):
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ✗ FAIL")
            if not has_min:
                print(f"    Expected at least {test['min_alternatives']}, got {len(alternatives)}")
            if test["should_contain"] and not has_expected:
                print(f"    Missing expected terms: {test['should_contain']}")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_generate_feedback():
    """Test feedback generation"""
    print("\n" + "=" * 80)
    print("TEST: Feedback Generation")
    print("=" * 80)
    
    test_cases = [
        {
            "topic": "Jugendschutz Baden-Württemberg 2025",
            "entity_count": 0,
            "should_contain": ["No entities found", "very specific", "Try searching"]
        },
        {
            "topic": "Jugendarmut Baden-Württemberg",
            "entity_count": 2,
            "should_contain": ["Only 2 entity", "low number"]
        },
        {
            "topic": "Paris France",
            "entity_count": 5,
            "should_contain": ["Found 5 entities", "good result"]
        }
    ]
    
    passed = 0
    for test in test_cases:
        topic = test["topic"]
        entity_count = test["entity_count"]
        feedback = generate_feedback(topic, entity_count)
        
        print(f"\nTopic: {topic}")
        print(f"  Entity Count: {entity_count}")
        print(f"  Feedback (first 200 chars):")
        print(f"    {feedback[:200]}...")
        
        # Check if expected phrases are present
        has_expected = all(phrase.lower() in feedback.lower() for phrase in test["should_contain"])
        
        if has_expected:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ✗ FAIL")
            missing = [p for p in test["should_contain"] if p.lower() not in feedback.lower()]
            print(f"    Missing phrases: {missing}")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_enhance_instructions():
    """Test instruction enhancement"""
    print("\n" + "=" * 80)
    print("TEST: Instruction Enhancement")
    print("=" * 80)
    
    base_instructions = """You are a research agent.

OUTPUT FORMAT:
Return JSON with entities.
"""
    
    test_cases = [
        {
            "topic": "Jugendschutz Baden-Württemberg 2025",
            "should_contain": ["MULTI-PASS SEARCH STRATEGY", "FALLBACK SEARCH TERMS", "Jugendschutz Baden-Württemberg"]
        },
        {
            "topic": "Paris France",
            "should_contain": ["MULTI-PASS SEARCH STRATEGY"]  # Should still get strategy even if broad
        }
    ]
    
    passed = 0
    for test in test_cases:
        topic = test["topic"]
        enhanced = enhance_instructions(topic, base_instructions)
        
        print(f"\nTopic: {topic}")
        print(f"  Original length: {len(base_instructions)} chars")
        print(f"  Enhanced length: {len(enhanced)} chars")
        print(f"  Added: {len(enhanced) - len(base_instructions)} chars")
        
        # Check if expected sections are present
        has_expected = all(phrase in enhanced for phrase in test["should_contain"])
        
        # Check that OUTPUT FORMAT is still present
        has_output_format = "OUTPUT FORMAT" in enhanced
        
        if has_expected and has_output_format:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ✗ FAIL")
            if not has_expected:
                missing = [p for p in test["should_contain"] if p not in enhanced]
                print(f"    Missing sections: {missing}")
            if not has_output_format:
                print("    Missing OUTPUT FORMAT section")
    
    print(f"\n{passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def main():
    """Run all unit tests"""
    print("=" * 80)
    print("SEARCH STRATEGY UNIT TESTS")
    print("=" * 80)
    print("\nTesting search strategy module without API server...")
    
    results = []
    
    # Run all tests
    results.append(("Topic Analysis", test_analyze_topic()))
    results.append(("Alternative Generation", test_generate_alternatives()))
    results.append(("Feedback Generation", test_generate_feedback()))
    results.append(("Instruction Enhancement", test_enhance_instructions()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} test suites passed\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("🎉 All unit tests passed!")
        print("\nNext step: Start API server and run integration tests:")
        print("  Terminal 1: poetry run python api/main.py")
        print("  Terminal 2: python tests/test_improved_prompts.py")
        return 0
    else:
        print("❌ Some unit tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
