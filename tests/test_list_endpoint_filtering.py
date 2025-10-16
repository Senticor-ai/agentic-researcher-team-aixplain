"""
Unit tests for the enhanced list endpoint with filtering and pagination
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.persistent_storage import PersistentAgentTeamStore
import tempfile
import os


@pytest.fixture
def temp_store():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    store = PersistentAgentTeamStore(db_path=db_path)
    
    # Create test teams
    store.create_team(
        topic="Kinderarmut in Deutschland",
        goals=["Find statistics", "Identify key organizations"],
        interaction_limit=50,
        mece_strategy="depth_first"
    )
    
    store.create_team(
        topic="Jugendarmut in Berlin",
        goals=["Research youth poverty"],
        interaction_limit=50,
        mece_strategy="depth_first"
    )
    
    store.create_team(
        topic="Climate Policy",
        goals=["Research climate policies"],
        interaction_limit=50,
        mece_strategy="depth_first"
    )
    
    # Set different statuses
    teams = store.get_all_teams()
    # Find teams by topic and set their status
    for team in teams:
        if "Kinderarmut" in team["topic"]:
            store.update_team_status(team["team_id"], "completed")
        elif "Jugendarmut" in team["topic"]:
            store.update_team_status(team["team_id"], "running")
        # Climate Policy stays as "pending"
    
    yield store
    
    # Cleanup
    os.unlink(db_path)


def test_get_teams_filtered_no_filters(temp_store):
    """Test getting teams without any filters"""
    teams = temp_store.get_teams_filtered()
    assert len(teams) == 3
    # Should be ordered by created_at DESC
    assert teams[0]["topic"] == "Climate Policy"


def test_get_teams_filtered_by_topic(temp_store):
    """Test filtering teams by topic substring"""
    teams = temp_store.get_teams_filtered(topic="armut")
    assert len(teams) == 2
    assert all("armut" in team["topic"].lower() for team in teams)


def test_get_teams_filtered_by_topic_case_insensitive(temp_store):
    """Test that topic filtering is case-insensitive"""
    teams_lower = temp_store.get_teams_filtered(topic="kinder")
    teams_upper = temp_store.get_teams_filtered(topic="KINDER")
    assert len(teams_lower) == len(teams_upper) == 1
    assert teams_lower[0]["topic"] == teams_upper[0]["topic"]


def test_get_teams_filtered_by_status(temp_store):
    """Test filtering teams by status"""
    completed_teams = temp_store.get_teams_filtered(status="completed")
    assert len(completed_teams) == 1
    assert completed_teams[0]["status"] == "completed"
    
    running_teams = temp_store.get_teams_filtered(status="running")
    assert len(running_teams) == 1
    assert running_teams[0]["status"] == "running"
    
    pending_teams = temp_store.get_teams_filtered(status="pending")
    assert len(pending_teams) == 1
    assert pending_teams[0]["status"] == "pending"


def test_get_teams_filtered_combined_filters(temp_store):
    """Test filtering with both topic and status"""
    teams = temp_store.get_teams_filtered(topic="armut", status="completed")
    assert len(teams) == 1
    assert "armut" in teams[0]["topic"].lower()
    assert teams[0]["status"] == "completed"


def test_get_teams_filtered_with_limit(temp_store):
    """Test pagination with limit"""
    teams = temp_store.get_teams_filtered(limit=2)
    assert len(teams) == 2


def test_get_teams_filtered_with_offset(temp_store):
    """Test pagination with offset"""
    all_teams = temp_store.get_teams_filtered(limit=10)
    first_page = temp_store.get_teams_filtered(limit=2, offset=0)
    second_page = temp_store.get_teams_filtered(limit=2, offset=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 1
    assert first_page[0]["team_id"] == all_teams[0]["team_id"]
    assert first_page[1]["team_id"] == all_teams[1]["team_id"]
    assert second_page[0]["team_id"] == all_teams[2]["team_id"]


def test_get_teams_filtered_no_matches(temp_store):
    """Test filtering with no matches"""
    teams = temp_store.get_teams_filtered(topic="nonexistent")
    assert len(teams) == 0


def test_get_teams_filtered_ordering(temp_store):
    """Test that results are ordered by created_at DESC"""
    teams = temp_store.get_teams_filtered()
    # Most recent should be first
    for i in range(len(teams) - 1):
        assert teams[i]["created_at"] >= teams[i + 1]["created_at"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
