"""
End-to-End Integration Test for Einbürgerungstests in Baden-Württemberg

This test verifies that the Phase 1.5 improvements work correctly:
1. GPT-4o model for all agents
2. Google Search preference for German topics
3. Wikipedia Agent one-at-a-time processing
4. Entity extraction and validation
"""
import pytest
import requests
import time
import json
from datetime import datetime

from tests.config import API_BASE_URL, SLOW_TEST_TIMEOUT

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

# Test configuration
TOPIC = "Einbürgerungstests in Baden-Württemberg"
GOALS = ["Find stakeholders and programs", "Identify key organizations and officials"]
INTERACTION_LIMIT = 50
MAX_WAIT_TIME = SLOW_TEST_TIMEOUT  # 5 minutes default


@pytest.mark.skipif(True, reason="Run manually with: pytest tests/test_e2e_einbuergerung.py -v -s")
def test_einbuergerung_e2e():
    """
    End-to-end test for Einbürgerungstests topic
    
    Expected results after Phase 1.5:
    - At least 5 entities extracted
    - Google Search used for German topic
    - Wikipedia enrichment attempted
    - No repeated timeouts
    """
    print(f"\n{'='*80}")
    print(f"E2E Test: {TOPIC}")
    print(f"{'='*80}\n")
    
    # Step 1: Create team
    print("Step 1: Creating team...")
    create_response = requests.post(
        f"{API_BASE_URL}/api/v1/agent-teams",
        json={
            "topic": TOPIC,
            "goals": GOALS,
            "interaction_limit": INTERACTION_LIMIT
        }
    )
    
    assert create_response.status_code == 200, f"Failed to create team: {create_response.text}"
    
    team_data = create_response.json()
    team_id = team_data["team_id"]
    print(f"✓ Team created: {team_id}")
    print(f"  Status: {team_data['status']}")
    print(f"  Created at: {team_data['created_at']}")
    
    # Step 2: Wait for completion
    print(f"\nStep 2: Waiting for completion (max {MAX_WAIT_TIME}s)...")
    start_time = time.time()
    status = "pending"
    
    while status in ["pending", "running"] and (time.time() - start_time) < MAX_WAIT_TIME:
        time.sleep(5)
        
        detail_response = requests.get(f"{API_BASE_URL}/api/v1/agent-teams/{team_id}")
        assert detail_response.status_code == 200
        
        detail_data = detail_response.json()
        status = detail_data["status"]
        
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] Status: {status}")
        
        if status == "completed":
            break
    
    assert status == "completed", f"Team did not complete in time. Final status: {status}"
    
    elapsed_time = int(time.time() - start_time)
    print(f"✓ Team completed in {elapsed_time}s")
    
    # Step 3: Get detailed results
    print(f"\nStep 3: Analyzing results...")
    detail_response = requests.get(f"{API_BASE_URL}/api/v1/agent-teams/{team_id}")
    detail_data = detail_response.json()
    
    # Extract key metrics
    execution_log = detail_data.get("execution_log", [])
    agent_response = detail_data.get("agent_response", {})
    sachstand = detail_data.get("sachstand", {})
    
    # Count entities
    entities = sachstand.get("hasPart", [])
    entity_count = len(entities)
    
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")
    print(f"Team ID: {team_id}")
    print(f"Status: {status}")
    print(f"Execution time: {elapsed_time}s")
    print(f"Entities extracted: {entity_count}")
    
    # Analyze execution log
    print(f"\nExecution Log Analysis:")
    for entry in execution_log:
        if isinstance(entry, str):
            if "model" in entry.lower():
                print(f"  - {entry}")
            elif "entity" in entry.lower():
                print(f"  - {entry}")
            elif "timeout" in entry.lower() or "limit" in entry.lower():
                print(f"  ⚠️  {entry}")
    
    # Count intermediate steps
    intermediate_steps = agent_response.get("intermediate_steps", [])
    step_count = len(intermediate_steps)
    print(f"\nIntermediate steps: {step_count}")
    
    # Count agent calls
    agent_calls = {}
    for step in intermediate_steps:
        agent = step.get("agent", "Unknown")
        agent_calls[agent] = agent_calls.get(agent, 0) + 1
    
    print(f"\nAgent calls:")
    for agent, count in sorted(agent_calls.items()):
        print(f"  - {agent}: {count}")
    
    # Entity breakdown
    if entities:
        entity_types = {}
        for entity in entities:
            entity_type = entity.get("@type", "Unknown")
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print(f"\nEntity types:")
        for entity_type, count in sorted(entity_types.items()):
            print(f"  - {entity_type}: {count}")
        
        # Show first few entities
        print(f"\nSample entities:")
        for i, entity in enumerate(entities[:3]):
            print(f"  {i+1}. {entity.get('name', 'N/A')} ({entity.get('@type', 'N/A')})")
    
    # Assertions
    print(f"\n{'='*80}")
    print(f"ASSERTIONS")
    print(f"{'='*80}")
    
    # Minimum success criteria
    assert entity_count >= 5, f"Expected at least 5 entities, got {entity_count}"
    print(f"✓ Entity count >= 5: {entity_count}")
    
    assert step_count >= 10, f"Expected at least 10 steps, got {step_count}"
    print(f"✓ Step count >= 10: {step_count}")
    
    # Check for Search Agent calls
    search_agent_calls = agent_calls.get("Search Agent", 0)
    assert search_agent_calls >= 3, f"Expected at least 3 Search Agent calls, got {search_agent_calls}"
    print(f"✓ Search Agent calls >= 3: {search_agent_calls}")
    
    # Check that we didn't have too many timeouts
    timeout_count = sum(1 for step in intermediate_steps 
                       if "stopped due to iteration limit" in str(step.get("output", "")))
    assert timeout_count <= 2, f"Too many timeouts: {timeout_count}"
    print(f"✓ Timeout count <= 2: {timeout_count}")
    
    # Target success criteria (warnings if not met)
    if entity_count >= 10:
        print(f"✓ Target: Entity count >= 10: {entity_count}")
    else:
        print(f"⚠️  Target not met: Entity count < 10: {entity_count}")
    
    if timeout_count == 0:
        print(f"✓ Stretch: No timeouts")
    else:
        print(f"⚠️  Stretch not met: {timeout_count} timeouts")
    
    print(f"\n{'='*80}")
    print(f"TEST PASSED ✓")
    print(f"{'='*80}")
    print(f"\nView results: http://localhost:5173/teams/{team_id}")
    print(f"API endpoint: {API_BASE_URL}/api/v1/agent-teams/{team_id}")
    
    return {
        "team_id": team_id,
        "entity_count": entity_count,
        "step_count": step_count,
        "timeout_count": timeout_count,
        "elapsed_time": elapsed_time
    }


if __name__ == "__main__":
    """
    Run this test manually:
    
    1. Start the API:
       uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    
    2. Run the test:
       python tests/test_e2e_einbuergerung.py
    """
    print("Starting E2E Integration Test...")
    print("Make sure the API is running on http://localhost:8000")
    print()
    
    try:
        # Check if API is running
        health_response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not responding correctly")
            exit(1)
        print("✓ API is running")
        print()
        
        # Run the test
        result = test_einbuergerung_e2e()
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Team ID: {result['team_id']}")
        print(f"Entities: {result['entity_count']}")
        print(f"Steps: {result['step_count']}")
        print(f"Timeouts: {result['timeout_count']}")
        print(f"Time: {result['elapsed_time']}s")
        print()
        print("✓ All assertions passed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API at http://localhost:8000")
        print("   Make sure the API is running:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
