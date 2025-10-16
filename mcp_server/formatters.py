"""
JSON-LD response formatters for MCP tools.

This module provides functions to format responses from the FastAPI backend
into JSON-LD format following schema.org vocabulary for LibreChat consumption.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def format_spawn_response(
    team_id: str,
    topic: str,
    created_at: str,
    status: str = "pending"
) -> Dict[str, Any]:
    """
    Format the response for spawn_agent_team tool.
    
    Args:
        team_id: Unique identifier for the spawned team
        topic: Research topic
        created_at: ISO 8601 timestamp of creation
        status: Current status (default: "pending")
        
    Returns:
        JSON-LD formatted response following schema.org Action type
    """
    logger.debug(f"Formatting spawn response for team_id={team_id}, topic='{topic}'")
    
    return {
        "@context": "https://schema.org",
        "@type": "Action",
        "actionStatus": "PotentialActionStatus",
        "object": {
            "@type": "ResearchReport",
            "identifier": team_id,
            "name": topic,
            "dateCreated": created_at,
            "status": status
        },
        "result": {
            "message": "Agent team spawned successfully. Use get_execution_status to check progress."
        }
    }


def format_status_response(
    team_id: str,
    topic: str,
    created_at: str,
    status: str,
    modified_at: Optional[str] = None,
    entity_count: Optional[int] = None,
    duration_seconds: Optional[float] = None
) -> Dict[str, Any]:
    """
    Format the response for get_execution_status tool.
    
    Args:
        team_id: Unique identifier for the team
        topic: Research topic
        created_at: ISO 8601 timestamp of creation
        status: Current status (pending, running, completed, failed)
        modified_at: ISO 8601 timestamp of last modification (optional)
        entity_count: Number of entities extracted (only for completed status)
        duration_seconds: Execution duration in seconds (only for completed status)
        
    Returns:
        JSON-LD formatted response following schema.org ResearchReport type
    """
    logger.debug(f"Formatting status response for team_id={team_id}, status={status}")
    
    response = {
        "@context": "https://schema.org",
        "@type": "ResearchReport",
        "identifier": team_id,
        "name": topic,
        "dateCreated": created_at,
        "status": status
    }
    
    # Add optional fields if provided
    if modified_at:
        response["dateModified"] = modified_at
    
    if entity_count is not None and status == "completed":
        response["numberOfEntities"] = entity_count
        logger.debug(f"Added entity count: {entity_count}")
    
    if duration_seconds is not None and status == "completed":
        # Convert seconds to ISO 8601 duration format (PT5M23S)
        response["duration"] = _format_iso8601_duration(duration_seconds)
        logger.debug(f"Added duration: {duration_seconds}s")
    
    return response


def format_list_response(
    teams: List[Dict[str, Any]],
    total_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Format the response for list_executions tool.
    
    Args:
        teams: List of team dictionaries from backend
        total_count: Total number of items (defaults to len(teams))
        
    Returns:
        JSON-LD formatted response following schema.org ItemList type
    """
    if total_count is None:
        total_count = len(teams)
    
    logger.debug(f"Formatting list response with {total_count} teams")
    
    item_list_elements = []
    for position, team in enumerate(teams, start=1):
        item = {
            "@type": "ResearchReport",
            "identifier": team.get("team_id", team.get("id", "")),
            "name": team.get("topic", ""),
            "dateCreated": team.get("created_at", ""),
            "status": team.get("status", "unknown")
        }
        
        # Add optional fields if present
        if "updated_at" in team or "modified_at" in team:
            item["dateModified"] = team.get("updated_at", team.get("modified_at"))
        
        # Add entity count if completed
        if team.get("status") == "completed":
            sachstand = team.get("sachstand")
            if sachstand and isinstance(sachstand, dict):
                entities = sachstand.get("hasPart", [])
                if entities:
                    item["numberOfEntities"] = len(entities)
        
        item_list_elements.append({
            "@type": "ListItem",
            "position": position,
            "item": item
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "numberOfItems": total_count,
        "itemListElement": item_list_elements
    }


def format_results_response(sachstand: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the response for get_execution_results tool.
    
    This function returns the sachstand JSON-LD as-is since it's already
    in the correct format. This function exists for consistency and to allow
    for future transformations if needed.
    
    Args:
        sachstand: JSON-LD sachstand from backend
        
    Returns:
        JSON-LD formatted sachstand (passed through)
    """
    entity_count = len(sachstand.get("hasPart", [])) if isinstance(sachstand, dict) else 0
    logger.debug(f"Formatting results response with {entity_count} entities")
    
    # The sachstand is already in JSON-LD format, so we return it as-is
    # This function exists for consistency and future extensibility
    return sachstand


def format_error_response(
    code: str,
    message: str,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format error responses in JSON-LD format.
    
    Args:
        code: Error code (e.g., "EXECUTION_NOT_FOUND", "BACKEND_UNAVAILABLE")
        message: Human-readable error message
        timestamp: ISO 8601 timestamp (defaults to current time)
        
    Returns:
        JSON-LD formatted error response
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    logger.debug(f"Formatting error response: code={code}, message='{message}'")
    
    return {
        "@context": "https://schema.org",
        "@type": "ErrorResponse",
        "error": {
            "code": code,
            "message": message,
            "timestamp": timestamp
        }
    }


def _format_iso8601_duration(seconds: float) -> str:
    """
    Convert seconds to ISO 8601 duration format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        ISO 8601 duration string (e.g., "PT5M23S", "PT1H30M45S")
    """
    total_seconds = int(seconds)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    parts = ["PT"]
    
    if hours > 0:
        parts.append(f"{hours}H")
    if minutes > 0:
        parts.append(f"{minutes}M")
    if secs > 0 or (hours == 0 and minutes == 0):
        parts.append(f"{secs}S")
    
    return "".join(parts)
