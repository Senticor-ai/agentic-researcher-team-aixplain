"""MCP server implementation for LibreChat integration.

This module implements the core MCP server that exposes tools for
spawning agent teams and retrieving historical execution data.

The server is completely stateless - all state is managed by the FastAPI backend.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from .fastapi_client import FastAPIClient
from .formatters import (
    format_spawn_response,
    format_status_response,
    format_list_response,
    format_results_response,
    format_error_response,
)

logger = logging.getLogger(__name__)


class LibreChatMCPServer:
    """Main MCP server for LibreChat integration.
    
    This server is completely stateless and acts as a thin translation layer
    between the MCP protocol and the FastAPI REST API. All data persistence
    and business logic remains in the FastAPI backend.
    
    The server exposes tools for:
    - Spawning agent teams for topic research
    - Checking execution status
    - Retrieving execution results
    - Listing historical executions
    """
    
    def __init__(self, api_base_url: str, timeout: float = 30.0):
        """Initialize the MCP server.
        
        Args:
            api_base_url: Base URL for the FastAPI backend (e.g., "http://localhost:8000")
            timeout: HTTP request timeout in seconds (default: 30.0)
        """
        self.fastapi_client = FastAPIClient(api_base_url, timeout=timeout)
        self.server = Server("librechat-osint-mcp")
        
        # Register tool handlers
        self._register_tools()
        
        logger.info(f"LibreChatMCPServer initialized with backend at {api_base_url} (timeout={timeout}s)")
    
    def _register_tools(self) -> None:
        """Register MCP tools with their handlers."""
        
        # Tool 1: spawn_agent_team
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="spawn_agent_team",
                    description=(
                        "Spawn an OSINT agent team to research a topic. "
                        "Returns immediately with execution ID. "
                        "Use get_execution_status to check progress."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Research topic (e.g., 'Kinderarmut in Deutschland')"
                            },
                            "goals": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional research goals"
                            },
                            "interaction_limit": {
                                "type": "integer",
                                "default": 50,
                                "description": "Maximum agent interactions before returning results"
                            }
                        },
                        "required": ["topic"]
                    }
                ),
                Tool(
                    name="get_execution_status",
                    description="Check the status of a running or completed execution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "execution_id": {
                                "type": "string",
                                "description": "Execution ID returned from spawn_agent_team"
                            }
                        },
                        "required": ["execution_id"]
                    }
                ),
                Tool(
                    name="get_execution_results",
                    description=(
                        "Get full JSON-LD results for a completed execution. "
                        "Returns error if not completed."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "execution_id": {
                                "type": "string",
                                "description": "Execution ID of completed execution"
                            }
                        },
                        "required": ["execution_id"]
                    }
                ),
                Tool(
                    name="list_executions",
                    description="List all executions with optional filtering and pagination",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topic_filter": {
                                "type": "string",
                                "description": "Filter by topic substring (case-insensitive)"
                            },
                            "status_filter": {
                                "type": "string",
                                "enum": ["pending", "running", "completed", "failed"],
                                "description": "Filter by execution status"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 10,
                                "description": "Maximum number of results (max 100)"
                            },
                            "offset": {
                                "type": "integer",
                                "default": 0,
                                "description": "Offset for pagination"
                            }
                        }
                    }
                )
            ]
        
        # Register call_tool handler
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool invocations."""
            logger.debug(f"Tool invoked: {name} with arguments: {arguments}")
            
            try:
                if name == "spawn_agent_team":
                    result = await self.spawn_agent_team(**arguments)
                elif name == "get_execution_status":
                    result = await self.get_execution_status(**arguments)
                elif name == "get_execution_results":
                    result = await self.get_execution_results(**arguments)
                elif name == "list_executions":
                    result = await self.list_executions(**arguments)
                else:
                    logger.warning(f"Unknown tool requested: {name}")
                    result = format_error_response(
                        "UNKNOWN_TOOL",
                        f"Unknown tool: {name}"
                    )
                
                logger.debug(f"Tool {name} completed successfully")
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}", exc_info=True)
                error_response = format_error_response(
                    "TOOL_EXECUTION_ERROR",
                    f"Error executing tool {name}: {str(e)}"
                )
                return [TextContent(type="text", text=json.dumps(error_response, ensure_ascii=False))]
    
    async def spawn_agent_team(
        self,
        topic: str,
        goals: Optional[List[str]] = None,
        interaction_limit: int = 50
    ) -> Dict[str, Any]:
        """Spawn a new agent team for topic research.
        
        Args:
            topic: Research topic
            goals: Optional list of research goals (defaults to empty list)
            interaction_limit: Maximum agent interactions (default: 50)
            
        Returns:
            JSON-LD response with execution ID and status
        """
        # Validate input parameters
        if not topic or not topic.strip():
            logger.warning("spawn_agent_team called with empty topic")
            return format_error_response(
                "INVALID_PARAMETER",
                "Topic parameter is required and cannot be empty"
            )
        
        if interaction_limit < 1 or interaction_limit > 1000:
            logger.warning(f"spawn_agent_team called with invalid interaction_limit: {interaction_limit}")
            return format_error_response(
                "INVALID_PARAMETER",
                "interaction_limit must be between 1 and 1000"
            )
        
        # Default goals to empty list if not provided
        if goals is None:
            goals = []
        
        logger.info(f"Spawning agent team for topic: '{topic}' with {len(goals)} goals and interaction_limit={interaction_limit}")
        
        try:
            # Call FastAPI backend to create team
            response = await self.fastapi_client.create_team(
                topic=topic,
                goals=goals,
                interaction_limit=interaction_limit
            )
            
            team_id = response["team_id"]
            logger.info(f"Agent team spawned successfully: team_id={team_id}")
            
            # Format response as JSON-LD
            return format_spawn_response(
                team_id=team_id,
                topic=topic,
                created_at=response["created_at"],
                status=response.get("status", "pending")
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while spawning team for topic '{topic}': {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to spawn agent team: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error while spawning team for topic '{topic}': {e}", exc_info=True)
            return format_error_response(
                "INTERNAL_ERROR",
                f"Unexpected error: {str(e)}"
            )
    
    async def get_execution_status(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """Get current status of an execution.
        
        Args:
            execution_id: Execution ID to check
            
        Returns:
            JSON-LD response with status and progress info
        """
        # Validate execution_id parameter
        if not execution_id or not execution_id.strip():
            logger.warning("get_execution_status called with empty execution_id")
            return format_error_response(
                "INVALID_PARAMETER",
                "execution_id parameter is required and cannot be empty"
            )
        
        logger.info(f"Getting status for execution: {execution_id}")
        
        try:
            # Call FastAPI backend to get team status
            team_data = await self.fastapi_client.get_team_status(execution_id)
            
            # Extract relevant fields
            topic = team_data.get("topic", "")
            created_at = team_data.get("created_at", "")
            updated_at = team_data.get("updated_at")
            status = team_data.get("status", "unknown")
            
            logger.debug(f"Execution {execution_id} status: {status}")
            
            # Calculate entity count if completed
            entity_count = None
            if status == "completed":
                sachstand = team_data.get("sachstand")
                if sachstand and isinstance(sachstand, dict):
                    entities = sachstand.get("hasPart", [])
                    entity_count = len(entities)
                    logger.debug(f"Execution {execution_id} has {entity_count} entities")
            
            # Calculate duration if completed
            duration_seconds = None
            if status == "completed" and created_at and updated_at:
                from datetime import datetime
                try:
                    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    duration_seconds = (updated - created).total_seconds()
                    logger.debug(f"Execution {execution_id} duration: {duration_seconds}s")
                except Exception as e:
                    logger.warning(f"Failed to calculate duration for {execution_id}: {e}")
            
            logger.info(f"Successfully retrieved status for execution {execution_id}: {status}")
            
            # Format response as JSON-LD
            return format_status_response(
                team_id=execution_id,
                topic=topic,
                created_at=created_at,
                status=status,
                modified_at=updated_at,
                entity_count=entity_count,
                duration_seconds=duration_seconds
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Execution not found: {execution_id}")
                return format_error_response(
                    "EXECUTION_NOT_FOUND",
                    f"Execution with ID {execution_id} not found"
                )
            logger.error(f"HTTP status error while getting status for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to get execution status: {str(e)}"
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while getting status for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to get execution status: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error while getting status for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "INTERNAL_ERROR",
                f"Unexpected error: {str(e)}"
            )
    
    async def get_execution_results(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """Get full JSON-LD results for a completed execution.
        
        Args:
            execution_id: Execution ID to retrieve results for
            
        Returns:
            Full JSON-LD Sachstand response
        """
        # Validate execution_id parameter
        if not execution_id or not execution_id.strip():
            logger.warning("get_execution_results called with empty execution_id")
            return format_error_response(
                "INVALID_PARAMETER",
                "execution_id parameter is required and cannot be empty"
            )
        
        logger.info(f"Getting results for execution: {execution_id}")
        
        try:
            # First check if execution is completed
            logger.debug(f"Checking status before retrieving results for {execution_id}")
            team_data = await self.fastapi_client.get_team_status(execution_id)
            status = team_data.get("status", "unknown")
            
            if status != "completed":
                logger.warning(f"Attempted to get results for incomplete execution {execution_id} (status: {status})")
                return format_error_response(
                    "EXECUTION_NOT_COMPLETED",
                    f"Execution is not completed yet. Current status: {status}. "
                    f"Use get_execution_status to check progress."
                )
            
            # Get the sachstand
            logger.debug(f"Retrieving sachstand for completed execution {execution_id}")
            sachstand_data = await self.fastapi_client.get_sachstand(execution_id)
            sachstand = sachstand_data.get("content")
            
            if not sachstand:
                logger.error(f"Sachstand content missing for completed execution {execution_id}")
                return format_error_response(
                    "RESULTS_NOT_AVAILABLE",
                    "Execution is completed but results are not available"
                )
            
            entity_count = len(sachstand.get("hasPart", [])) if isinstance(sachstand, dict) else 0
            logger.info(f"Successfully retrieved results for execution {execution_id} ({entity_count} entities)")
            
            # Return the sachstand as-is (already in JSON-LD format)
            return format_results_response(sachstand)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Execution not found when getting results: {execution_id}")
                return format_error_response(
                    "EXECUTION_NOT_FOUND",
                    f"Execution with ID {execution_id} not found"
                )
            logger.error(f"HTTP status error while getting results for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to get execution results: {str(e)}"
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while getting results for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to get execution results: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error while getting results for {execution_id}: {e}", exc_info=True)
            return format_error_response(
                "INTERNAL_ERROR",
                f"Unexpected error: {str(e)}"
            )
    
    async def list_executions(
        self,
        topic_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List executions with filtering and pagination.
        
        Args:
            topic_filter: Filter by topic substring (case-insensitive)
            status_filter: Filter by execution status
            limit: Maximum number of results (default: 10, max: 100)
            offset: Offset for pagination (default: 0)
            
        Returns:
            JSON-LD ItemList with execution summaries
        """
        # Validate filter parameters
        if limit < 1 or limit > 100:
            logger.warning(f"list_executions called with invalid limit: {limit}")
            return format_error_response(
                "INVALID_PARAMETER",
                "limit must be between 1 and 100"
            )
        
        if offset < 0:
            logger.warning(f"list_executions called with invalid offset: {offset}")
            return format_error_response(
                "INVALID_PARAMETER",
                "offset must be non-negative"
            )
        
        if status_filter and status_filter not in ["pending", "running", "completed", "failed"]:
            logger.warning(f"list_executions called with invalid status_filter: {status_filter}")
            return format_error_response(
                "INVALID_PARAMETER",
                f"Invalid status_filter: {status_filter}. "
                f"Must be one of: pending, running, completed, failed"
            )
        
        logger.info(
            f"Listing executions (topic_filter={topic_filter}, "
            f"status_filter={status_filter}, limit={limit}, offset={offset})"
        )
        
        try:
            # Call FastAPI backend to list teams
            teams = await self.fastapi_client.list_teams(
                topic_filter=topic_filter,
                status_filter=status_filter,
                limit=limit,
                offset=offset
            )
            
            logger.info(f"Successfully retrieved {len(teams)} executions")
            logger.debug(f"Execution IDs: {[team.get('team_id') for team in teams]}")
            
            # Format response as JSON-LD ItemList
            return format_list_response(teams)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while listing executions: {e}", exc_info=True)
            return format_error_response(
                "BACKEND_ERROR",
                f"Failed to list executions: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error while listing executions: {e}", exc_info=True)
            return format_error_response(
                "INTERNAL_ERROR",
                f"Unexpected error: {str(e)}"
            )
