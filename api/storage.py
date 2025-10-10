"""
In-memory storage for agent teams
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4


class AgentTeamStore:
    """In-memory storage for agent teams"""
    
    def __init__(self):
        self._teams: Dict[str, dict] = {}
    
    def create_team(self, topic: str, goals: list, interaction_limit: int, mece_strategy: str) -> dict:
        """Create a new agent team"""
        team_id = str(uuid4())
        now = datetime.now(timezone.utc)
        
        team = {
            "team_id": team_id,
            "topic": topic,
            "goals": goals,
            "status": "pending",
            "interaction_limit": interaction_limit,
            "mece_strategy": mece_strategy,
            "created_at": now,
            "updated_at": now,
            "execution_log": [],
            "aixplain_agent_id": None,  # Will be set when agent is created
            "agent_response": None,  # Will store agent output
            "sachstand": None  # Will store JSON-LD Sachstand
        }
        
        self._teams[team_id] = team
        return team
    
    def set_aixplain_agent_id(self, team_id: str, agent_id: str) -> bool:
        """Set the aixplain agent ID for a team"""
        if team_id in self._teams:
            self._teams[team_id]["aixplain_agent_id"] = agent_id
            self._teams[team_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False
    
    def set_agent_response(self, team_id: str, response: dict) -> bool:
        """Set the agent response for a team"""
        if team_id in self._teams:
            self._teams[team_id]["agent_response"] = response
            self._teams[team_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False
    
    def set_sachstand(self, team_id: str, sachstand: dict) -> bool:
        """Set the JSON-LD Sachstand for a team"""
        if team_id in self._teams:
            self._teams[team_id]["sachstand"] = sachstand
            self._teams[team_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False
    
    def get_team(self, team_id: str) -> Optional[dict]:
        """Get team by ID"""
        return self._teams.get(team_id)
    
    def get_all_teams(self) -> list:
        """Get all teams"""
        return list(self._teams.values())
    
    def update_team_status(self, team_id: str, status: str) -> bool:
        """Update team status"""
        if team_id in self._teams:
            self._teams[team_id]["status"] = status
            self._teams[team_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False
    
    def add_log_entry(self, team_id: str, log_entry: str) -> bool:
        """Add log entry to team"""
        if team_id in self._teams:
            self._teams[team_id]["execution_log"].append(log_entry)
            self._teams[team_id]["updated_at"] = datetime.now(timezone.utc)
            return True
        return False


# Global storage instance
_store: Optional[AgentTeamStore] = None


def get_store() -> AgentTeamStore:
    """Get storage instance (singleton)"""
    global _store
    if _store is None:
        _store = AgentTeamStore()
    return _store
