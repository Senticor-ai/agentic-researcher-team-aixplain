"""
Persistent storage for agent teams using SQLite
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class PersistentAgentTeamStore:
    """Persistent storage for agent teams using SQLite"""
    
    def __init__(self, db_path: str = None):
        """Initialize storage with SQLite database"""
        import os
        if db_path is None:
            db_path = os.getenv("DB_PATH", "./data/teams.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"Initialized persistent storage at {self.db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    team_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    goals TEXT NOT NULL,
                    status TEXT NOT NULL,
                    interaction_limit INTEGER NOT NULL,
                    mece_strategy TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    execution_log TEXT NOT NULL,
                    aixplain_agent_id TEXT,
                    agent_response TEXT,
                    sachstand TEXT,
                    mece_graph TEXT,
                    model_id TEXT,
                    model_name TEXT,
                    duration_seconds REAL,
                    git_sha TEXT,
                    git_repo_url TEXT
                )
            """)
            conn.commit()
            
            # Add new columns to existing tables if they don't exist
            new_columns = [
                ("mece_graph", "TEXT"),
                ("model_id", "TEXT"),
                ("model_name", "TEXT"),
                ("duration_seconds", "REAL"),
                ("git_sha", "TEXT"),
                ("git_repo_url", "TEXT"),
                ("raw_agent_response", "TEXT"),
                ("server_logs", "TEXT")
            ]
            
            for column_name, column_type in new_columns:
                try:
                    conn.execute(f"ALTER TABLE teams ADD COLUMN {column_name} {column_type}")
                    conn.commit()
                except sqlite3.OperationalError:
                    # Column already exists
                    pass
    
    def _serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string"""
        return dt.isoformat()
    
    def _deserialize_datetime(self, dt_str: str) -> datetime:
        """Deserialize ISO format string to datetime"""
        return datetime.fromisoformat(dt_str)
    
    def _team_to_dict(self, row: tuple) -> dict:
        """Convert database row to team dictionary"""
        return {
            "team_id": row[0],
            "topic": row[1],
            "goals": json.loads(row[2]),
            "status": row[3],
            "interaction_limit": row[4],
            "mece_strategy": row[5],
            "created_at": self._deserialize_datetime(row[6]),
            "updated_at": self._deserialize_datetime(row[7]),
            "execution_log": json.loads(row[8]),
            "aixplain_agent_id": row[9],
            "agent_response": json.loads(row[10]) if row[10] else None,
            "sachstand": json.loads(row[11]) if row[11] else None,
            "mece_graph": json.loads(row[12]) if len(row) > 12 and row[12] else None,
            "model_id": row[13] if len(row) > 13 else None,
            "model_name": row[14] if len(row) > 14 else None,
            "duration_seconds": row[15] if len(row) > 15 else None,
            "git_sha": row[16] if len(row) > 16 else None,
            "git_repo_url": row[17] if len(row) > 17 else None,
            "raw_agent_response": row[18] if len(row) > 18 and row[18] else None,
            "server_logs": json.loads(row[19]) if len(row) > 19 and row[19] else [],
        }
    
    def create_team(self, topic: str, goals: list, interaction_limit: int, mece_strategy: str, 
                   model_id: str = None, model_name: str = None, git_sha: str = None, git_repo_url: str = None) -> dict:
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
            "aixplain_agent_id": None,
            "agent_response": None,
            "sachstand": None,
            "mece_graph": None,
            "model_id": model_id,
            "model_name": model_name,
            "duration_seconds": None,
            "git_sha": git_sha,
            "git_repo_url": git_repo_url
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO teams (
                    team_id, topic, goals, status, interaction_limit, mece_strategy,
                    created_at, updated_at, execution_log, aixplain_agent_id,
                    agent_response, sachstand, mece_graph, model_id, model_name,
                    duration_seconds, git_sha, git_repo_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id,
                topic,
                json.dumps(goals),
                "pending",
                interaction_limit,
                mece_strategy,
                self._serialize_datetime(now),
                self._serialize_datetime(now),
                json.dumps([]),
                None,
                None,
                None,
                None,
                model_id,
                model_name,
                None,
                git_sha,
                git_repo_url
            ))
            conn.commit()
        
        logger.info(f"Created team {team_id}: {topic}")
        return team
    
    def set_aixplain_agent_id(self, team_id: str, agent_id: str, request_id: str = None) -> bool:
        """Set the aixplain agent ID and optional request ID for a team"""
        team = self.get_team(team_id)
        if not team:
            return False
        
        # Store request_id in execution_log as a special entry
        if request_id:
            execution_log = team["execution_log"]
            execution_log.append({
                "type": "request_id",
                "request_id": request_id,
                "timestamp": self._serialize_datetime(datetime.now(timezone.utc))
            })
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE teams 
                    SET aixplain_agent_id = ?, execution_log = ?, updated_at = ?
                    WHERE team_id = ?
                """, (agent_id, json.dumps(execution_log), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
                conn.commit()
                return cursor.rowcount > 0
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE teams 
                    SET aixplain_agent_id = ?, updated_at = ?
                    WHERE team_id = ?
                """, (agent_id, self._serialize_datetime(datetime.now(timezone.utc)), team_id))
                conn.commit()
                return cursor.rowcount > 0
    
    def get_request_id(self, team_id: str) -> Optional[str]:
        """Get the request ID for a team from execution log"""
        team = self.get_team(team_id)
        if not team:
            return None
        
        execution_log = team.get("execution_log", [])
        for entry in reversed(execution_log):  # Check from most recent
            if isinstance(entry, dict) and entry.get("type") == "request_id":
                return entry.get("request_id")
        
        return None
    
    def set_agent_response(self, team_id: str, response: dict) -> bool:
        """Set the agent response for a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE teams 
                SET agent_response = ?, updated_at = ?
                WHERE team_id = ?
            """, (json.dumps(response), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def set_raw_agent_response(self, team_id: str, raw_response: str) -> bool:
        """Set the raw unprocessed agent response for a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE teams 
                SET raw_agent_response = ?, updated_at = ?
                WHERE team_id = ?
            """, (raw_response, self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def set_sachstand(self, team_id: str, sachstand: dict) -> bool:
        """Set the JSON-LD Sachstand for a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE teams 
                SET sachstand = ?, updated_at = ?
                WHERE team_id = ?
            """, (json.dumps(sachstand), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def set_mece_graph(self, team_id: str, mece_graph: dict) -> bool:
        """Set the MECE graph for a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE teams 
                SET mece_graph = ?, updated_at = ?
                WHERE team_id = ?
            """, (json.dumps(mece_graph), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_server_log(self, team_id: str, log_entry: dict) -> bool:
        """Add a server log entry for a team"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current logs
            cursor = conn.execute("SELECT server_logs FROM teams WHERE team_id = ?", (team_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            current_logs = json.loads(row[0]) if row[0] else []
            current_logs.append(log_entry)
            
            # Update with new log
            cursor = conn.execute("""
                UPDATE teams 
                SET server_logs = ?, updated_at = ?
                WHERE team_id = ?
            """, (json.dumps(current_logs), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_mece_graph(self, team_id: str) -> Optional[dict]:
        """Get the MECE graph for a team"""
        team = self.get_team(team_id)
        return team.get("mece_graph") if team else None
    
    def update_mece_node_status(self, team_id: str, node_id: str, status: str, entities_found: int = 0) -> bool:
        """Update the status of a specific MECE node"""
        team = self.get_team(team_id)
        if not team or not team.get("mece_graph"):
            return False
        
        mece_graph = team["mece_graph"]
        nodes = mece_graph.get("nodes", [])
        
        # Find and update the node
        updated = False
        for node in nodes:
            if node.get("id") == node_id:
                node["status"] = status
                if entities_found > 0:
                    node["entities_found"] = entities_found
                updated = True
                break
        
        if updated:
            # Recalculate completion percentage
            total_nodes = len(nodes)
            completed_nodes = sum(1 for node in nodes if node.get("status") == "complete")
            mece_graph["completion_percentage"] = int((completed_nodes / total_nodes) * 100) if total_nodes > 0 else 0
            mece_graph["remaining_nodes"] = [node["id"] for node in nodes if node.get("status") != "complete"]
            
            return self.set_mece_graph(team_id, mece_graph)
        
        return False
    
    def get_team(self, team_id: str) -> Optional[dict]:
        """Get team by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM teams WHERE team_id = ?
            """, (team_id,))
            row = cursor.fetchone()
            return self._team_to_dict(row) if row else None
    
    def get_all_teams(self) -> List[dict]:
        """Get all teams, ordered by created_at descending (newest first)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM teams ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [self._team_to_dict(row) for row in rows]
    
    def get_teams_filtered(
        self, 
        topic: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """
        Get teams with optional filtering and pagination
        
        Args:
            topic: Filter by topic substring (case-insensitive)
            status: Filter by exact status match
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
        
        Returns:
            List of team dictionaries matching the filters
        """
        query = "SELECT * FROM teams WHERE 1=1"
        params = []
        
        # Add topic filter (case-insensitive substring match)
        if topic:
            query += " AND LOWER(topic) LIKE LOWER(?)"
            params.append(f"%{topic}%")
        
        # Add status filter (exact match)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        # Add ordering and pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._team_to_dict(row) for row in rows]
    
    def update_team_status(self, team_id: str, status: str) -> bool:
        """Update team status and calculate duration if completing"""
        team = self.get_team(team_id)
        if not team:
            return False
        
        now = datetime.now(timezone.utc)
        duration_seconds = None
        
        # Calculate duration when completing
        if status in ['completed', 'failed'] and team.get('duration_seconds') is None:
            created_at = team['created_at']
            duration_seconds = (now - created_at).total_seconds()
        
        with sqlite3.connect(self.db_path) as conn:
            if duration_seconds is not None:
                cursor = conn.execute("""
                    UPDATE teams 
                    SET status = ?, updated_at = ?, duration_seconds = ?
                    WHERE team_id = ?
                """, (status, self._serialize_datetime(now), duration_seconds, team_id))
            else:
                cursor = conn.execute("""
                    UPDATE teams 
                    SET status = ?, updated_at = ?
                    WHERE team_id = ?
                """, (status, self._serialize_datetime(now), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_log_entry(self, team_id: str, log_entry: str) -> bool:
        """Add log entry to team"""
        team = self.get_team(team_id)
        if not team:
            return False
        
        execution_log = team["execution_log"]
        execution_log.append(log_entry)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE teams 
                SET execution_log = ?, updated_at = ?
                WHERE team_id = ?
            """, (json.dumps(execution_log), self._serialize_datetime(datetime.now(timezone.utc)), team_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_team(self, team_id: str) -> bool:
        """Delete a team (optional, for cleanup)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM teams WHERE team_id = ?
            """, (team_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_teams_by_status(self, status: str) -> List[dict]:
        """Get teams by status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM teams WHERE status = ? ORDER BY created_at DESC
            """, (status,))
            rows = cursor.fetchall()
            return [self._team_to_dict(row) for row in rows]
    
    def get_recent_teams(self, limit: int = 10) -> List[dict]:
        """Get most recent teams"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM teams ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._team_to_dict(row) for row in rows]


# Global storage instance
_store: Optional[PersistentAgentTeamStore] = None


def get_store() -> PersistentAgentTeamStore:
    """Get storage instance (singleton)"""
    global _store
    if _store is None:
        _store = PersistentAgentTeamStore()
    return _store
