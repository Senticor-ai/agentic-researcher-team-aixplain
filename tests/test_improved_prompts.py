"""
Test improved entity extraction prompts

This script tests the refined prompts with topics that previously failed:
1. German topics (Jugendschutz Baden-Württemberg)
2. Simple topics (Paris France)
3. Government topics (Sozialer Lagebericht)

Run with: python tests/test_improved_prompts.py
"""
import requests
import json
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

# Test cases with expected improvements
TEST_CASES = [
    {
        "name": "Simple Well-Known Topic",
        "topic": "Paris France",
        "goals": [
            "Find key organizations in Paris",
            "Identify important officials",
            "Locate tourist and cultural institutions"
        ],
        "expected_min_entities": 3,
        "notes": "Should work - simple, well-documented topic"
    },
    {
        "name": "German Government Topic",
        "topic": "Jugendschutz Baden-Württemberg 2025",
        "goals": [
            "Find organizations working on youth protection",
            "Identify government officials responsible",
            "Locate relevant agencies and departments"
        ],
        "expected_min_entities": 2,
        "notes": "Previously failed - testing German language support"
    },
    {
        "name": "German Social Topic",
        "topic": "Jugendarmut Baden-Württemberg",
        "goals": [
            "Find NGOs working on youth poverty",
            "Identify government programs and officials",
            "Locate welfare organizations"
        ],
        "expected_min_entities": 3,
        "notes": "Previously had placeholder URLs - testing real source requirement"
    },
    {
        "name": "Specific German Official",
        "topic": "Dr. Manfred Lucha Baden-Württemberg",
        "goals": [
            "Find information about this minister",
            "Identify his ministry and role",
            "Locate official sources"
        ],
        "expected_min_entities": 2,
        "notes": "Person search - should find minister and ministry"
    }
]


def run_test_case(test_case):
    """Run a single test case"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_case['name']}")
    print("=" * 80)
    print(f"Topic: {test_case['topic']}")
    print(f"Goals: {len(test_case['goals'])} objectives")
    print(f"Expected: At least {test_case['expected_min_entities']} entities")
    print(f"Notes: {test_case['notes']}")
    print()
    
    # Create agent team
    try:
        response = requests.post(
            f"{API_BASE}/agent-teams",
            json={
                "topic": test_case["topic"],
                "goals": test_case["goals"]
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        team_id = data["team_id"]
        print(f"✓ Created team: {team_id}")
    except Exception as e:
        print(f"✗ Failed to create team: {e}")
        return {
            "test_name": test_case["name"],
            "status": "error",
            "error": str(e)
        }
    
    # Wait for completion (max 2 minutes)
    max_wait = 120
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{API_BASE}/agent-teams/{team_id}", timeout=10)
            response.raise_for_status()
            team_data = response.json()
            status = team_data["status"]
            
            if status == "completed":
                print(f"✓ Team completed in {int(time.time() - start_time)}s")
                break
            elif status == "failed":
                print(f"✗ Team failed")
                return {
                    "test_name": test_case["name"],
                    "status": "failed",
                    "team_id": team_id,
                    "execution_log": team_data.get("execution_log", [])
                }
            
            time.sleep(5)
        except Exception as e:
            print(f"✗ Error polling status: {e}")
            return {
                "test_name": test_case["name"],
                "status": "error",
                "error": str(e)
            }
    else:
        print(f"⏱ Timeout after {max_wait}s")
        return {
            "test_name": test_case["name"],
            "status": "timeout",
            "team_id": team_id
        }
    
    # Analyze results
    sachstand = team_data.get("sachstand", {})
    entities = sachstand.get("hasPart", [])
    
    print(f"\n📊 RESULTS:")
    print(f"   Entities extracted: {len(entities)}")
    print(f"   Expected minimum: {test_case['expected_min_entities']}")
    
    # Check if we met expectations
    success = len(entities) >= test_case["expected_min_entities"]
    
    if entities:
        # Analyze entity quality
        people = [e for e in entities if e.get("@type") == "Person"]
        orgs = [e for e in entities if e.get("@type") == "Organization"]
        
        print(f"   - People: {len(people)}")
        print(f"   - Organizations: {len(orgs)}")
        
        # Check for placeholder URLs
        placeholder_count = 0
        real_sources = set()
        
        for entity in entities:
            print(f"\n   {entity.get('@type')}: {entity.get('name')}")
            if entity.get("description"):
                desc = entity.get("description", "")[:100]
                print(f"      Description: {desc}...")
            
            citations = entity.get("citation", [])
            for citation in citations:
                url = citation.get("url", "")
                if "example.com" in url or "test.com" in url:
                    placeholder_count += 1
                    print(f"      ⚠️  Placeholder URL: {url}")
                else:
                    real_sources.add(url)
                    print(f"      ✓ Real source: {url}")
        
        print(f"\n   Source Quality:")
        print(f"   - Real sources: {len(real_sources)}")
        print(f"   - Placeholder URLs: {placeholder_count}")
        
        # Quality check
        has_placeholders = placeholder_count > 0
        
        if success and not has_placeholders:
            print(f"\n✅ TEST PASSED")
            result_status = "passed"
        elif success and has_placeholders:
            print(f"\n⚠️  TEST PARTIAL PASS (has placeholder URLs)")
            result_status = "partial"
        else:
            print(f"\n✗ TEST FAILED (insufficient entities)")
            result_status = "failed"
    else:
        print(f"\n✗ TEST FAILED (no entities extracted)")
        result_status = "failed"
    
    return {
        "test_name": test_case["name"],
        "status": result_status,
        "team_id": team_id,
        "entities_count": len(entities),
        "expected_min": test_case["expected_min_entities"],
        "people_count": len(people) if entities else 0,
        "orgs_count": len(orgs) if entities else 0,
        "real_sources": len(real_sources) if entities else 0,
        "placeholder_urls": placeholder_count if entities else 0
    }


def main():
    """Run all test cases"""
    print("=" * 80)
    print("TESTING IMPROVED ENTITY EXTRACTION PROMPTS")
    print("=" * 80)
    print(f"\nRunning {len(TEST_CASES)} test cases...")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("✗ API server not responding correctly")
            return 1
        print("✓ API server is running\n")
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        print("\nPlease start the server first:")
        print("   poetry run python api/main.py")
        return 1
    
    # Run all test cases
    results = []
    for test_case in TEST_CASES:
        result = run_test_case(test_case)
        results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] in ["failed", "timeout", "error"])
    
    print(f"\nResults:")
    print(f"  ✅ Passed: {passed}/{len(results)}")
    print(f"  ⚠️  Partial: {partial}/{len(results)}")
    print(f"  ✗ Failed: {failed}/{len(results)}")
    
    print(f"\nDetailed Results:")
    for result in results:
        status_icon = {
            "passed": "✅",
            "partial": "⚠️ ",
            "failed": "✗",
            "timeout": "⏱ ",
            "error": "❌"
        }.get(result["status"], "?")
        
        print(f"\n{status_icon} {result['test_name']}")
        if result["status"] in ["passed", "partial", "failed"]:
            print(f"   Entities: {result.get('entities_count', 0)} (expected: {result.get('expected_min', 0)})")
            print(f"   People: {result.get('people_count', 0)}, Organizations: {result.get('orgs_count', 0)}")
            print(f"   Real sources: {result.get('real_sources', 0)}, Placeholders: {result.get('placeholder_urls', 0)}")
        elif result["status"] == "error":
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    # Save results
    output_file = "tests/improved_prompts_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Full results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    
    # Return exit code
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    elif passed + partial == len(results):
        print("⚠️  All tests passed or partially passed")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
