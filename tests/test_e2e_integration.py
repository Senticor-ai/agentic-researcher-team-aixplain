"""
End-to-end integration tests for API and UI
Tests the full flow from API endpoints to ensure UI can consume them
"""
import pytest
import requests
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class TestE2EIntegration:
    """End-to-end integration tests"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_cors_headers(self):
        """Test CORS headers are present for UI"""
        response = requests.options(
            f"{API_BASE}/agent-teams",
            headers={
                "Origin": "http://localhost:5174",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should not be blocked
        assert response.status_code in [200, 204]
    
    def test_create_and_list_teams(self):
        """Test creating a team and listing it"""
        # Create a team
        create_payload = {
            "topic": "E2E Test Topic",
            "goals": ["Test goal 1", "Test goal 2"]
        }
        
        create_response = requests.post(
            f"{API_BASE}/agent-teams",
            json=create_payload
        )
        assert create_response.status_code == 200
        
        created_team = create_response.json()
        assert "team_id" in created_team
        assert created_team["status"] in ["pending", "initializing", "running"]
        assert "created_at" in created_team
        
        team_id = created_team["team_id"]
        
        # List teams - should include our new team
        list_response = requests.get(f"{API_BASE}/agent-teams")
        assert list_response.status_code == 200
        
        teams = list_response.json()
        assert isinstance(teams, list)
        assert len(teams) > 0
        
        # Find our team in the list
        our_team = next((t for t in teams if t["team_id"] == team_id), None)
        assert our_team is not None
        assert our_team["topic"] == "E2E Test Topic"
        assert our_team["status"] in ["initializing", "running", "completed", "failed"]
    
    def test_get_team_detail(self):
        """Test getting team details"""
        # Create a team first
        create_payload = {
            "topic": "Detail Test Topic",
            "goals": ["Detail test goal"]
        }
        
        create_response = requests.post(
            f"{API_BASE}/agent-teams",
            json=create_payload
        )
        assert create_response.status_code == 200
        team_id = create_response.json()["team_id"]
        
        # Get team details
        detail_response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
        assert detail_response.status_code == 200
        
        team_detail = detail_response.json()
        assert team_detail["team_id"] == team_id
        assert team_detail["topic"] == "Detail Test Topic"
        assert team_detail["goals"] == "Detail test goal"
        assert "execution_log" in team_detail
        assert isinstance(team_detail["execution_log"], list)
        assert "created_at" in team_detail
        assert "updated_at" in team_detail
    
    def test_team_execution_flow(self):
        """Test the full team execution flow"""
        # Create a team
        create_payload = {
            "topic": "Flow Test Topic",
            "goals": ["Flow test goal"]
        }
        
        create_response = requests.post(
            f"{API_BASE}/agent-teams",
            json=create_payload
        )
        assert create_response.status_code == 200
        team_id = create_response.json()["team_id"]
        
        # Wait a bit for background task to start
        time.sleep(1)
        
        # Check team detail - should have execution log entries
        detail_response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
        assert detail_response.status_code == 200
        
        team_detail = detail_response.json()
        assert len(team_detail["execution_log"]) > 0
        
        # Status should be pending, initializing, running, completed, or failed
        assert team_detail["status"] in ["pending", "initializing", "running", "completed", "failed"]
    
    def test_invalid_team_id(self):
        """Test getting non-existent team returns 404"""
        response = requests.get(f"{API_BASE}/agent-teams/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_team_validation(self):
        """Test team creation with invalid data"""
        # Missing required topic field
        invalid_payload = {
            "goals": ["Some goals"]
        }
        
        response = requests.post(
            f"{API_BASE}/agent-teams",
            json=invalid_payload
        )
        assert response.status_code == 422  # Validation error
    
    def test_ui_data_format(self):
        """Test that API returns data in format expected by UI"""
        # Create a team
        create_payload = {
            "topic": "UI Format Test",
            "goals": ["Test UI data format"]
        }
        
        create_response = requests.post(
            f"{API_BASE}/agent-teams",
            json=create_payload
        )
        team_id = create_response.json()["team_id"]
        
        # Get team detail
        detail_response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
        team = detail_response.json()
        
        # Verify UI-required fields are present
        assert "team_id" in team
        assert "topic" in team
        assert "status" in team
        assert "created_at" in team
        assert "execution_log" in team
        
        # Verify date format is parseable by JavaScript
        created_at = team["created_at"]
        # Should be ISO format
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # Verify execution_log is array
        assert isinstance(team["execution_log"], list)
        
        # Verify optional fields have correct types when present
        if team.get("sachstand"):
            assert isinstance(team["sachstand"], dict)
        
        if team.get("agent_response"):
            assert isinstance(team["agent_response"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
