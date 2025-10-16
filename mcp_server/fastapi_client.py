"""
FastAPI client for backend communication.

This client handles HTTP communication with the existing FastAPI backend
to spawn agent teams and retrieve execution data.
"""
import logging
from typing import Any, Dict, List, Optional

import httpx


logger = logging.getLogger(__name__)


class FastAPIClient:
    """Client for communicating with the FastAPI backend."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize FastAPI client.
        
        Args:
            base_url: Base URL of the FastAPI backend (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info(f"Initialized FastAPIClient with base_url={self.base_url}")
    
    async def create_team(
        self,
        topic: str,
        goals: List[str],
        interaction_limit: int = 50,
        mece_strategy: str = "depth_first"
    ) -> Dict[str, Any]:
        """
        Create a new agent team for research.
        
        Calls POST /api/v1/agent-teams to spawn a new agent team.
        The team will run in the background and return immediately.
        
        Args:
            topic: Research topic
            goals: List of research goals
            interaction_limit: Maximum agent interactions (default: 50)
            mece_strategy: MECE decomposition strategy (default: "depth_first")
            
        Returns:
            Dict containing team_id, status, and created_at
            
        Raises:
            httpx.HTTPError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/api/v1/agent-teams"
        payload = {
            "topic": topic,
            "goals": goals,
            "interaction_limit": interaction_limit,
            "mece_strategy": mece_strategy
        }
        
        logger.debug(f"Creating team: POST {url} with payload={payload}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Team created successfully: team_id={data.get('team_id')}")
                return data
                
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout while creating team: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while creating team: {e}")
            raise
    
    async def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """
        Get detailed status of an agent team.
        
        Calls GET /api/v1/agent-teams/{team_id} to retrieve full team details
        including status, execution log, and results if completed.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Dict containing team details including status, execution_log, sachstand, etc.
            
        Raises:
            httpx.HTTPError: If the request fails (including 404 if team not found)
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/api/v1/agent-teams/{team_id}"
        
        logger.debug(f"Getting team status: GET {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Retrieved team status: team_id={team_id}, status={data.get('status')}")
                return data
                
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout while getting team status: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while getting team status: {e}")
            raise
    
    async def get_sachstand(self, team_id: str) -> Dict[str, Any]:
        """
        Get JSON-LD Sachstand for a completed agent team.
        
        Calls GET /api/v1/sachstand/{team_id} to retrieve the JSON-LD output.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Dict containing file_path and content (JSON-LD sachstand)
            
        Raises:
            httpx.HTTPError: If the request fails (including 404 if not found or not ready)
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/api/v1/sachstand/{team_id}"
        
        logger.debug(f"Getting sachstand: GET {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Retrieved sachstand: team_id={team_id}")
                return data
                
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout while getting sachstand: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while getting sachstand: {e}")
            raise
    
    async def list_teams(
        self,
        topic_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all agent teams with optional filtering and pagination.
        
        Calls GET /api/v1/agent-teams to retrieve all teams.
        If the backend doesn't support filtering via query parameters,
        this method applies client-side filtering.
        
        Args:
            topic_filter: Filter by topic substring (case-insensitive)
            status_filter: Filter by status (pending, running, completed, failed)
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            List of team dictionaries with metadata
            
        Raises:
            httpx.HTTPError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        url = f"{self.base_url}/api/v1/agent-teams"
        
        # Try to pass filters as query parameters (backend may support them)
        params = {}
        if topic_filter is not None:
            params["topic"] = topic_filter
        if status_filter is not None:
            params["status"] = status_filter
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        
        logger.debug(f"Listing teams: GET {url} with params={params}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Backend may return a list directly or wrapped in a response object
                teams = data if isinstance(data, list) else data.get("teams", [])
                
                # Apply client-side filtering if backend doesn't support it
                # (Backend may ignore unknown query parameters)
                filtered_teams = teams
                
                if topic_filter is not None:
                    topic_lower = topic_filter.lower()
                    filtered_teams = [
                        team for team in filtered_teams
                        if topic_lower in team.get("topic", "").lower()
                    ]
                
                if status_filter is not None:
                    filtered_teams = [
                        team for team in filtered_teams
                        if team.get("status") == status_filter
                    ]
                
                # Apply client-side pagination if needed
                if offset is not None:
                    filtered_teams = filtered_teams[offset:]
                if limit is not None:
                    filtered_teams = filtered_teams[:limit]
                
                logger.info(f"Retrieved {len(filtered_teams)} teams (filtered from {len(teams)} total)")
                return filtered_teams
                
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout while listing teams: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while listing teams: {e}")
            raise
