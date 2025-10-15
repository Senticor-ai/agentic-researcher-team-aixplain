"""
End-to-End Test: Lagebericht zur Kinderarmut in Baden-Württemberg

This script tests the complete flow:
1. Create an agent team for researching child poverty report stakeholders
2. Wait for agent execution
3. Verify we get results back

Run this test with a valid AIXPLAIN_API_KEY in your .env file:
    python tests/e2e_test_kinderarmut.py
"""
import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Import test configuration
from tests.config import API_BASE_URL, POLL_INTERVAL, DEFAULT_TIMEOUT

# Configuration
MAX_WAIT_TIME = DEFAULT_TIMEOUT  # seconds


def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv("AIXPLAIN_API_KEY")
    if not api_key or api_key == "your_aixplain_api_key_here":
        print("❌ ERROR: AIXPLAIN_API_KEY not configured in .env file")
        print("Please set a valid API key before running this test.")
        return False
    print(f"✅ API key configured: {api_key[:10]}...")
    return True


def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: API server not running at {API_BASE_URL}")
        print(f"   Error: {e}")
        print("\nPlease start the server first:")
        print("   poetry run python api/main.py")
        return False
    return False


def create_agent_team():
    """Create agent team for Kinderarmut research"""
    print("\n📝 Creating agent team for Kinderarmut research...")
    
    request_data = {
        "topic": "Lagebericht zur Kinderarmut in Baden-Württemberg",
        "goals": [
            "Identify NGOs working on child poverty in Baden-Württemberg",
            "Find press organizations covering child poverty issues",
            "Discover think tanks researching child poverty",
            "Locate relevant federal and state publications",
            "Extract key stakeholder organizations and contacts"
        ],
        "interaction_limit": 50,
        "mece_strategy": "depth_first"
    }
    
    print(f"   Topic: {request_data['topic']}")
    print(f"   Goals: {len(request_data['goals'])} research objectives")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/agent-teams",
            json=request_data,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Agent team created: {data['team_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Created at: {data['created_at']}")
        
        return data['team_id']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to create agent team")
        print(f"   Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


def poll_team_status(team_id):
    """Poll team status until completion or timeout"""
    print(f"\n⏳ Polling team status (max {MAX_WAIT_TIME}s)...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < MAX_WAIT_TIME:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/agent-teams/{team_id}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            status = data['status']
            
            # Print status change
            if status != last_status:
                elapsed = int(time.time() - start_time)
                print(f"   [{elapsed}s] Status: {status}")
                
                # Print latest log entries
                if data.get('execution_log'):
                    for log_entry in data['execution_log'][-3:]:
                        print(f"      📋 {log_entry}")
                
                last_status = status
            
            # Check if completed or failed
            if status == "completed":
                print(f"✅ Agent execution completed!")
                return data
            elif status == "failed":
                print(f"❌ Agent execution failed!")
                print(f"   Execution log:")
                for log_entry in data.get('execution_log', []):
                    print(f"      {log_entry}")
                return data
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: Failed to poll team status")
            print(f"   Error: {e}")
            return None
    
    print(f"⏱️  Timeout: Agent did not complete within {MAX_WAIT_TIME}s")
    return None


def analyze_results(team_data):
    """Analyze and display results"""
    print("\n📊 Results Analysis:")
    print("=" * 60)
    
    print(f"\nTeam ID: {team_data['team_id']}")
    print(f"Topic: {team_data['topic']}")
    print(f"Status: {team_data['status']}")
    print(f"Created: {team_data['created_at']}")
    print(f"Updated: {team_data['updated_at']}")
    
    print(f"\n📋 Execution Log ({len(team_data.get('execution_log', []))} entries):")
    for i, log_entry in enumerate(team_data.get('execution_log', []), 1):
        print(f"   {i}. {log_entry}")
    
    # Check if we have agent response
    agent_response = team_data.get('agent_response')
    if agent_response:
        print(f"\n🤖 Agent Response:")
        print(f"   Agent ID: {agent_response.get('agent_id', 'N/A')}")
        print(f"   Status: {agent_response.get('status', 'N/A')}")
        print(f"\n   Output:")
        output = agent_response.get('output', '')
        if output:
            # Print first 500 chars
            print(f"   {output[:500]}...")
            if len(output) > 500:
                print(f"   ... ({len(output) - 500} more characters)")
        else:
            print("   (No output)")
    else:
        print(f"\n⚠️  No agent response available")
    
    # Save full results to file
    output_file = "tests/e2e_results_kinderarmut.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(team_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 Full results saved to: {output_file}")
    
    print("\n" + "=" * 60)


def create_expected_honeycomb_structure():
    """Create expected honeycomb JSON structure"""
    expected = {
        "@context": "https://schema.org",
        "@type": "ResearchProject",
        "name": "Lagebericht zur Kinderarmut in Baden-Württemberg",
        "description": "OSINT research on child poverty report stakeholders in Baden-Württemberg",
        "goals": [
            "Identify NGOs working on child poverty",
            "Find press organizations covering child poverty",
            "Discover think tanks researching child poverty",
            "Locate relevant publications"
        ],
        "stakeholders": {
            "organizations": [
                {
                    "@type": "Organization",
                    "name": "Example NGO",
                    "description": "NGO working on child poverty",
                    "url": "https://example.org",
                    "category": "NGO"
                }
            ],
            "persons": [
                {
                    "@type": "Person",
                    "name": "Example Person",
                    "jobTitle": "Director",
                    "affiliation": "Example Organization",
                    "url": "https://example.org/person"
                }
            ]
        },
        "sources": [
            {
                "@type": "WebPage",
                "name": "Ministry Website",
                "url": "https://example.gov",
                "category": "government"
            }
        ]
    }
    
    output_file = "tests/expected_honeycomb_kinderarmut.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(expected, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Expected honeycomb structure saved to: {output_file}")
    return expected


def main():
    """Main test execution"""
    print("=" * 60)
    print("End-to-End Test: Kinderarmut Research")
    print("=" * 60)
    
    # Pre-flight checks
    if not check_api_key():
        return 1
    
    if not check_api_server():
        return 1
    
    # Create expected structure
    print("\n📄 Creating expected honeycomb structure...")
    create_expected_honeycomb_structure()
    
    # Create agent team
    team_id = create_agent_team()
    if not team_id:
        return 1
    
    # Poll for completion
    team_data = poll_team_status(team_id)
    if not team_data:
        return 1
    
    # Analyze results
    analyze_results(team_data)
    
    # Final status
    if team_data.get('status') == 'completed':
        print("\n✅ End-to-end test PASSED")
        return 0
    else:
        print("\n❌ End-to-end test FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
