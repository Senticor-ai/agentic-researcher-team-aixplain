#!/usr/bin/env python3
"""
Manual test script for Wikipedia integration (bypasses pytest mocks)

Run with: poetry run python tests/manual_wikipedia_test.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Verify API key
if not os.getenv("TEAM_API_KEY"):
    print("ERROR: TEAM_API_KEY not found in environment")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from api.team_config import TeamConfig
from aixplain.factories import ToolFactory

def test_wikipedia_tool_id():
    """Test 1: Verify Wikipedia tool ID is configured"""
    print("\n" + "="*80)
    print("TEST 1: Wikipedia Tool ID Configuration")
    print("="*80)
    
    wikipedia_tool_id = TeamConfig.TOOL_IDS.get("wikipedia")
    
    if wikipedia_tool_id:
        print(f"✓ Wikipedia tool ID configured: {wikipedia_tool_id}")
        return True
    else:
        print("✗ Wikipedia tool ID NOT configured")
        return False


def test_wikipedia_tool_access():
    """Test 2: Verify Wikipedia tool can be accessed"""
    print("\n" + "="*80)
    print("TEST 2: Wikipedia Tool Access")
    print("="*80)
    
    try:
        wikipedia_tool = ToolFactory.get("6633fd59821ee31dd914e232")
        print(f"✓ Wikipedia tool retrieved successfully")
        print(f"  Tool name: {wikipedia_tool.name}")
        print(f"  Tool ID: {wikipedia_tool.id}")
        return True
    except Exception as e:
        print(f"✗ Failed to retrieve Wikipedia tool: {e}")
        return False


def test_wikipedia_agent_creation():
    """Test 3: Verify Wikipedia agent can be created"""
    print("\n" + "="*80)
    print("TEST 3: Wikipedia Agent Creation")
    print("="*80)
    
    try:
        wikipedia_agent = TeamConfig.create_wikipedia_agent(model="testing")
        
        if wikipedia_agent is None:
            print("✗ Wikipedia agent was not created (returned None)")
            return False
        
        print(f"✓ Wikipedia agent created successfully")
        print(f"  Agent name: {wikipedia_agent.name}")
        print(f"  Agent ID: {wikipedia_agent.id}")
        return True
    except Exception as e:
        print(f"✗ Failed to create Wikipedia agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_team_with_wikipedia():
    """Test 4: Verify team can be created with Wikipedia agent"""
    print("\n" + "="*80)
    print("TEST 4: Team Creation with Wikipedia Agent")
    print("="*80)
    
    try:
        topic = "Dr. Manfred Lucha Baden-Württemberg"
        goals = ["Find biographical information"]
        
        team = TeamConfig.create_team(
            topic=topic,
            goals=goals,
            model="testing",
            enable_wikipedia=True
        )
        
        print(f"✓ Team created successfully")
        print(f"  Team name: {team.name}")
        print(f"  Team ID: {team.id}")
        return True
    except Exception as e:
        print(f"✗ Failed to create team: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wikipedia_search():
    """Test 5: Test Wikipedia tool search functionality"""
    print("\n" + "="*80)
    print("TEST 5: Wikipedia Tool Search")
    print("="*80)
    
    try:
        wikipedia_tool = ToolFactory.get("6633fd59821ee31dd914e232")
        
        search_query = "Manfred Lucha"
        print(f"Searching Wikipedia for: '{search_query}'")
        
        result = wikipedia_tool.run({"text": search_query})
        
        print(f"✓ Wikipedia search completed")
        print(f"  Result type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"  Result keys: {list(result.keys())}")
            if "data" in result:
                print(f"  Data preview: {str(result['data'])[:200]}...")
        else:
            print(f"  Result preview: {str(result)[:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Wikipedia search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WIKIPEDIA INTEGRATION MANUAL TESTS")
    print("="*80)
    print("\nThese tests verify Wikipedia tool integration without pytest mocks.")
    
    results = []
    
    # Run tests
    results.append(("Tool ID Configuration", test_wikipedia_tool_id()))
    results.append(("Tool Access", test_wikipedia_tool_access()))
    results.append(("Agent Creation", test_wikipedia_agent_creation()))
    results.append(("Team Creation", test_team_with_wikipedia()))
    results.append(("Wikipedia Search", test_wikipedia_search()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Wikipedia integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
