"""
Tests for the Management API (V1 - DEPRECATED)

These tests are for the old single-agent architecture.
See test_api_integration.py for V2 team agent tests.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from api.main import app
from api.storage import get_store

# V1 tests - skipping as we've moved to V2 team agent architecture
pytestmark = [
    pytest.mark.unit,
    pytest.mark.skip(reason="V1 API tests deprecated - see test_api_integration.py for V2")
]


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset storage before each test"""
    store = get_store()
    store._teams.clear()
    yield


client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "honeycomb-osint-api"


@patch('api.main.run_agent_task')
def test_create_agent_team(mock_run_agent):
    """Test creating an agent team"""
    request_data = {
        "topic": "Dr. Manfred Lucha biography",
        "goals": ["Extract biographical information", "Identify key positions"]
    }
    
    response = client.post("/api/v1/agent-teams", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "team_id" in data
    assert data["status"] == "pending"
    assert "created_at" in data


@patch('api.main.run_agent_task')
def test_list_agent_teams(mock_run_agent):
    """Test listing all agent teams"""
    # Create a team first
    request_data = {
        "topic": "Test topic",
        "goals": ["Goal 1", "Goal 2"]
    }
    client.post("/api/v1/agent-teams", json=request_data)
    
    # List teams
    response = client.get("/api/v1/agent-teams")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["topic"] == "Test topic"
    assert data[0]["status"] == "pending"


@patch('api.main.run_agent_task')
def test_get_agent_team_detail(mock_run_agent):
    """Test getting detailed agent team information"""
    # Create a team first
    request_data = {
        "topic": "Integration policies",
        "goals": ["Identify stakeholders", "Timeline of changes"],
        "interaction_limit": 30
    }
    create_response = client.post("/api/v1/agent-teams", json=request_data)
    team_id = create_response.json()["team_id"]
    
    # Get team detail
    response = client.get(f"/api/v1/agent-teams/{team_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["team_id"] == team_id
    assert data["topic"] == "Integration policies"
    assert data["goals"] == ["Identify stakeholders", "Timeline of changes"]
    assert data["status"] == "pending"
    assert data["interaction_limit"] == 30
    assert data["mece_strategy"] == "depth_first"
    assert isinstance(data["execution_log"], list)


def test_get_nonexistent_team():
    """Test getting a team that doesn't exist"""
    response = client.get("/api/v1/agent-teams/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
