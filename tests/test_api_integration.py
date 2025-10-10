"""
Integration tests for API with team agent
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_agent_team():
    """Test creating an agent team"""
    response = client.post(
        "/api/v1/agent-teams",
        json={
            "topic": "Test Topic",
            "goals": ["Test Goal 1", "Test Goal 2"],
            "interaction_limit": 50,
            "mece_strategy": "depth_first"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "team_id" in data
    assert data["status"] == "pending"
    assert "created_at" in data


def test_list_agent_teams():
    """Test listing agent teams"""
    # Create a team first
    create_response = client.post(
        "/api/v1/agent-teams",
        json={
            "topic": "Test Topic",
            "goals": ["Test Goal"],
        }
    )
    assert create_response.status_code == 200
    
    # List teams
    response = client.get("/api/v1/agent-teams")
    assert response.status_code == 200
    teams = response.json()
    assert isinstance(teams, list)
    assert len(teams) > 0


def test_get_agent_team():
    """Test getting specific agent team"""
    # Create a team first
    create_response = client.post(
        "/api/v1/agent-teams",
        json={
            "topic": "Test Topic",
            "goals": ["Test Goal"],
        }
    )
    assert create_response.status_code == 200
    team_id = create_response.json()["team_id"]
    
    # Get team details
    response = client.get(f"/api/v1/agent-teams/{team_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["team_id"] == team_id
    assert data["topic"] == "Test Topic"
    assert data["goals"] == ["Test Goal"]


def test_get_nonexistent_team():
    """Test getting non-existent team returns 404"""
    response = client.get("/api/v1/agent-teams/nonexistent-id")
    assert response.status_code == 404
