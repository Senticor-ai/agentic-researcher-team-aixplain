"""
Custom logging handler to capture server logs for teams
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from contextvars import ContextVar

# Context variable to track current team_id
current_team_id: ContextVar[Optional[str]] = ContextVar('current_team_id', default=None)


class TeamLogHandler(logging.Handler):
    """Custom handler that captures logs and stores them per team"""
    
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setLevel(logging.INFO)
        
    def emit(self, record):
        """Emit a log record"""
        try:
            team_id = current_team_id.get()
            if not team_id:
                # No team context, skip
                return
            
            # Format the log entry
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Store in database
            self.store.add_server_log(team_id, log_entry)
            
        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)


def set_team_context(team_id: str):
    """Set the current team context for logging"""
    current_team_id.set(team_id)


def clear_team_context():
    """Clear the team context"""
    current_team_id.set(None)
