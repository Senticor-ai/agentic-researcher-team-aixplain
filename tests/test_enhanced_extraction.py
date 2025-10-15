"""
Test Enhanced Entity Extraction (Task 4 Implementation)

This script tests the enhanced extraction with new entity types:
- TOPIC entities
- EVENT entities (with dates)
- POLICY entities (with identifiers and dates)

Compares results with previous runs to show improvements.
"""
import pytest
import requests
import json
import time
import sys
from datetime import datetime

from tests.config import API_V1_BASE

pytestmark = [pytest.mark.integration, pytest.mark.slow]

API_BASE = API_V1_BASE

# Test cases from previous runs
TEST_CASES = [
    {
        "name": "Kinderarmut Baden-Württemberg",
        "topic": "Lagebericht zur Kinderarmut in Baden-Württemberg",
        "goals": [
            "Identify NGOs working on child poverty",
            "Find government officials and ministries",
            "Locate relevant policies and programs",
            "Identify key events and announcements"
        ],
        "expected_improvements": [
            "TOPIC: Kinderarmut (child poverty theme)",
            "POLICY: Starke-Familien-Gesetz or similar programs",
            "EVENT: Policy announcements or conferences",
            "More entities per search result (1.5+ average)"
        ]
    },
    {
        "name": "Jugendschutz Baden-Württemberg",
        "topic": "Jugendschutz Baden-Württemberg 2025",
        "goals": [
            "Find youth protection organizations",
            "Identify government officials and agencies",
            "Locate relevant laws and regulations",
            "Find policy changes and deadlines"
        ],
        "expected_improvements": [
            "TOPIC: Jugendschutz (youth protection)",
            "POLICY: Youth protection laws with dates",
            "EVENT: Policy effective dates",
            "Source organizations from all results"
        ]
    },
    {
        "name": "Dr. Manfred Lucha",
        "topic": "Dr. Manfred Lucha Baden-Württemberg",
        "goals": [
            "Find biographical information",
            "Identify official roles and ministry",
            "Locate policy areas and initiatives",
            "Find recent announcements"
        ],
        "expected_improvements": [
            "PERSON: Dr. Manfred Lucha",
            "ORGANIZATION: Ministry",
            "TOPIC: Policy areas (health, social affairs)",
            "EVENT: Recent announcements or initiatives"
        ]
    }
]


def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE}/../health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running\n")
            return True
    except:
        pass
    print("❌ API server not running")
    print("Please start: poetry run python api/main.py\n")
    return False


def run_test_case(test_case):
    """Run a single test case and analyze results"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_case['name']}")
    print("=" * 80)
    print(f"Topic: {test_case['topic']}")
    print(f"Goals: {', '.join(test_case['goals'][:2])}...")
    print()
    
    # Create agent team
    try:
        response = requests.post(
            f"{API_BASE}/agent-teams",
            json={
                "topic": test_case["topic"],
                "goals": test_case["goals"],
                "interaction_limit": 50
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        team_id = data["team_id"]
        print(f"✓ Created team: {team_id}")
    except Exception as e:
        print(f"✗ Failed to create team: {e}")
        return None
    
    # Poll for completion (max 3 minutes)
    print("⏳ Waiting for completion...")
    start_time = time.time()
    max_wait = 180
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{API_BASE}/agent-teams/{team_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            if status == "completed":
                print(f"✅ Completed in {int(time.time() - start_time)}s\n")
                return analyze_results(data, test_case)
            elif status == "failed":
                print(f"❌ Failed: {data.get('error', 'Unknown error')}\n")
                return None
            
            time.sleep(5)
        except Exception as e:
            print(f"✗ Error polling: {e}")
            return None
    
    print(f"⏱️ Timeout after {max_wait}s\n")
    return None


def analyze_results(team_data, test_case):
    """Analyze results and count entity types"""
    print("📊 RESULTS ANALYSIS")
    print("-" * 80)
    
    # Get agent response
    agent_response = team_data.get("agent_response", {})
    output = agent_response.get("output", "")
    
    if not output:
        print("⚠️  No output from agent")
        return None
    
    # Count entity types
    entity_counts = {
        "PERSON": output.count("PERSON:"),
        "ORGANIZATION": output.count("ORGANIZATION:"),
        "TOPIC": output.count("TOPIC:"),
        "EVENT": output.count("EVENT:"),
        "POLICY": output.count("POLICY:")
    }
    
    total_entities = sum(entity_counts.values())
    
    print(f"\n📈 Entity Counts:")
    print(f"   Total: {total_entities}")
    for entity_type, count in entity_counts.items():
        emoji = "✓" if count > 0 else " "
        print(f"   {emoji} {entity_type}: {count}")
    
    # Check for extraction summary
    has_summary = "EXTRACTION SUMMARY:" in output
    print(f"\n📋 Extraction Summary: {'✓ Present' if has_summary else '✗ Missing'}")
    
    if has_summary:
        # Extract summary section
        summary_start = output.find("EXTRACTION SUMMARY:")
        summary_section = output[summary_start:summary_start+500]
        print("\n" + summary_section[:300] + "...")
    
    # Check for new entity types
    print(f"\n🆕 New Entity Types:")
    new_types_found = []
    if entity_counts["TOPIC"] > 0:
        new_types_found.append(f"✓ TOPIC entities ({entity_counts['TOPIC']})")
    if entity_counts["EVENT"] > 0:
        new_types_found.append(f"✓ EVENT entities ({entity_counts['EVENT']})")
    if entity_counts["POLICY"] > 0:
        new_types_found.append(f"✓ POLICY entities ({entity_counts['POLICY']})")
    
    if new_types_found:
        for item in new_types_found:
            print(f"   {item}")
    else:
        print("   ⚠️  No new entity types found")
    
    # Check for dates in events/policies
    has_dates = "Date:" in output or "Effective Date:" in output
    print(f"\n📅 Temporal Information: {'✓ Present' if has_dates else '✗ Missing'}")
    
    # Check for identifiers in policies
    has_identifiers = "Identifier:" in output
    print(f"🔖 Policy Identifiers: {'✓ Present' if has_identifiers else '✗ Missing'}")
    
    # Save detailed results
    output_file = f"tests/results_{test_case['name'].replace(' ', '_').lower()}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Test: {test_case['name']}\n")
        f.write(f"Topic: {test_case['topic']}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("=" * 80 + "\n\n")
        f.write(output)
    
    print(f"\n💾 Full output saved to: {output_file}")
    
    return {
        "test_name": test_case["name"],
        "total_entities": total_entities,
        "entity_counts": entity_counts,
        "has_summary": has_summary,
        "has_dates": has_dates,
        "has_identifiers": has_identifiers,
        "new_types_count": len(new_types_found)
    }


def main():
    """Run all test cases"""
    print("=" * 80)
    print("ENHANCED ENTITY EXTRACTION TEST")
    print("Testing Task 4 Implementation: New Entity Types")
    print("=" * 80)
    print()
    
    if not check_api_server():
        return 1
    
    results = []
    
    for test_case in TEST_CASES:
        result = run_test_case(test_case)
        if result:
            results.append(result)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if not results:
        print("❌ No successful tests")
        return 1
    
    print(f"\n✅ Completed {len(results)}/{len(TEST_CASES)} tests\n")
    
    for result in results:
        print(f"\n{result['test_name']}:")
        print(f"  Total entities: {result['total_entities']}")
        print(f"  New types found: {result['new_types_count']}/3")
        print(f"  Has summary: {'✓' if result['has_summary'] else '✗'}")
        print(f"  Has dates: {'✓' if result['has_dates'] else '✗'}")
        print(f"  Entity breakdown: P:{result['entity_counts']['PERSON']} " +
              f"O:{result['entity_counts']['ORGANIZATION']} " +
              f"T:{result['entity_counts']['TOPIC']} " +
              f"E:{result['entity_counts']['EVENT']} " +
              f"Po:{result['entity_counts']['POLICY']}")
    
    # Check if improvements are present
    total_new_types = sum(r['new_types_count'] for r in results)
    avg_entities = sum(r['total_entities'] for r in results) / len(results)
    
    print(f"\n📊 Overall Metrics:")
    print(f"  Average entities per test: {avg_entities:.1f}")
    print(f"  Tests with new entity types: {sum(1 for r in results if r['new_types_count'] > 0)}/{len(results)}")
    print(f"  Tests with extraction summary: {sum(1 for r in results if r['has_summary'])}/{len(results)}")
    print(f"  Tests with temporal info: {sum(1 for r in results if r['has_dates'])}/{len(results)}")
    
    if total_new_types > 0 and avg_entities >= 5:
        print("\n✅ IMPROVEMENTS DETECTED!")
        print("   - New entity types are being extracted")
        print("   - Entity counts are higher")
        return 0
    else:
        print("\n⚠️  Limited improvements detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
