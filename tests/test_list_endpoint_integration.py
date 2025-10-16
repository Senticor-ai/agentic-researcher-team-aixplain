"""
Test script for the enhanced list endpoint with filtering and pagination
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_teams_no_filters():
    """Test listing teams without any filters"""
    print("\n=== Test 1: List teams without filters ===")
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Found {len(teams)} teams")
        for team in teams[:3]:  # Show first 3
            print(f"  - {team['topic']} ({team['status']})")
    else:
        print(f"Error: {response.text}")

def test_list_teams_with_topic_filter():
    """Test listing teams with topic filter"""
    print("\n=== Test 2: List teams with topic filter ===")
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?topic=Kinder")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Found {len(teams)} teams matching 'Kinder'")
        for team in teams:
            print(f"  - {team['topic']} ({team['status']})")
    else:
        print(f"Error: {response.text}")

def test_list_teams_with_status_filter():
    """Test listing teams with status filter"""
    print("\n=== Test 3: List teams with status filter ===")
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?status=completed")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Found {len(teams)} completed teams")
        for team in teams[:3]:  # Show first 3
            print(f"  - {team['topic']} ({team['status']})")
    else:
        print(f"Error: {response.text}")

def test_list_teams_with_combined_filters():
    """Test listing teams with multiple filters"""
    print("\n=== Test 4: List teams with combined filters ===")
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?topic=armut&status=completed")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Found {len(teams)} completed teams matching 'armut'")
        for team in teams:
            print(f"  - {team['topic']} ({team['status']})")
    else:
        print(f"Error: {response.text}")

def test_list_teams_with_pagination():
    """Test listing teams with pagination"""
    print("\n=== Test 5: List teams with pagination ===")
    
    # First page
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?limit=2&offset=0")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Page 1: Found {len(teams)} teams")
        for team in teams:
            print(f"  - {team['topic']} ({team['status']})")
    
    # Second page
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?limit=2&offset=2")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Page 2: Found {len(teams)} teams")
        for team in teams:
            print(f"  - {team['topic']} ({team['status']})")

def test_list_teams_limit_enforcement():
    """Test that limit is enforced (max 100)"""
    print("\n=== Test 6: Test limit enforcement ===")
    response = requests.get(f"{BASE_URL}/api/v1/agent-teams?limit=200")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        teams = response.json()
        print(f"Requested 200, got {len(teams)} teams (max 100 enforced)")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Testing enhanced list endpoint...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    try:
        test_list_teams_no_filters()
        test_list_teams_with_topic_filter()
        test_list_teams_with_status_filter()
        test_list_teams_with_combined_filters()
        test_list_teams_with_pagination()
        test_list_teams_limit_enforcement()
        
        print("\n=== All tests completed ===")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to FastAPI server.")
        print("Please start the server with: ./start-backend.sh")
    except Exception as e:
        print(f"\nError: {e}")
