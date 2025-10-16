"""
Unit tests for FastAPIClient.

Tests cover:
- Successful requests and response parsing
- Error handling (404, 500, timeout)
- HTTP request mocking using httpx mock
"""
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from mcp_server.fastapi_client import FastAPIClient


@pytest.fixture
def client():
    """Create a FastAPIClient instance for testing."""
    return FastAPIClient(base_url="http://localhost:8000", timeout=30.0)


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


class TestFastAPIClientInit:
    """Tests for FastAPIClient initialization."""
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        client = FastAPIClient(base_url="http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"
    
    def test_init_sets_timeout(self):
        """Test that timeout is set correctly."""
        client = FastAPIClient(base_url="http://localhost:8000", timeout=60.0)
        assert client.timeout == 60.0
    
    def test_init_default_timeout(self):
        """Test that default timeout is 30.0 seconds."""
        client = FastAPIClient(base_url="http://localhost:8000")
        assert client.timeout == 30.0


class TestCreateTeam:
    """Tests for create_team method."""
    
    @pytest.mark.asyncio
    async def test_create_team_success(self, client):
        """Test successful team creation."""
        # Mock response data
        mock_response_data = {
            "team_id": "test-team-123",
            "status": "pending",
            "created_at": "2025-10-16T10:00:00Z"
        }
        
        # Create mock response
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data  # Regular function returning data
        mock_response.raise_for_status = lambda: None  # Regular function, not async
        
        # Create mock client
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        # Patch httpx.AsyncClient
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.create_team(
                topic="Test Topic",
                goals=["Goal 1", "Goal 2"],
                interaction_limit=50
            )
        
        # Verify the result
        assert result == mock_response_data
        assert result["team_id"] == "test-team-123"
        assert result["status"] == "pending"
        
        # Verify the request was made correctly
        mock_client.post.assert_called_once_with(
            "http://localhost:8000/api/v1/agent-teams",
            json={
                "topic": "Test Topic",
                "goals": ["Goal 1", "Goal 2"],
                "interaction_limit": 50,
                "mece_strategy": "depth_first"
            }
        )
    
    @pytest.mark.asyncio
    async def test_create_team_with_custom_strategy(self, client):
        """Test team creation with custom MECE strategy."""
        mock_response_data = {"team_id": "test-team-456", "status": "pending"}
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.create_team(
                topic="Test Topic",
                goals=["Goal 1"],
                interaction_limit=100,
                mece_strategy="breadth_first"
            )
        
        # Verify custom strategy was passed
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["mece_strategy"] == "breadth_first"
        assert call_args[1]["json"]["interaction_limit"] == 100
    
    @pytest.mark.asyncio
    async def test_create_team_http_404_error(self, client):
        """Test handling of 404 error during team creation."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Not Found",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.create_team(
                    topic="Test Topic",
                    goals=["Goal 1"]
                )
    
    @pytest.mark.asyncio
    async def test_create_team_http_500_error(self, client):
        """Test handling of 500 error during team creation."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.create_team(
                    topic="Test Topic",
                    goals=["Goal 1"]
                )
    
    @pytest.mark.asyncio
    async def test_create_team_timeout(self, client):
        """Test handling of timeout during team creation."""
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.TimeoutException):
                await client.create_team(
                    topic="Test Topic",
                    goals=["Goal 1"]
                )


class TestGetTeamStatus:
    """Tests for get_team_status method."""
    
    @pytest.mark.asyncio
    async def test_get_team_status_success(self, client):
        """Test successful retrieval of team status."""
        mock_response_data = {
            "team_id": "test-team-123",
            "topic": "Test Topic",
            "status": "completed",
            "created_at": "2025-10-16T10:00:00Z",
            "updated_at": "2025-10-16T10:05:00Z",
            "execution_log": ["Step 1", "Step 2"],
            "sachstand": {"@type": "ResearchReport"}
        }
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_team_status("test-team-123")
        
        assert result == mock_response_data
        assert result["team_id"] == "test-team-123"
        assert result["status"] == "completed"
        
        mock_client.get.assert_called_once_with(
            "http://localhost:8000/api/v1/agent-teams/test-team-123"
        )
    
    @pytest.mark.asyncio
    async def test_get_team_status_pending(self, client):
        """Test retrieval of pending team status."""
        mock_response_data = {
            "team_id": "test-team-456",
            "status": "pending",
            "created_at": "2025-10-16T10:00:00Z"
        }
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_team_status("test-team-456")
        
        assert result["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_team_status_404_error(self, client):
        """Test handling of 404 error when team not found."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Not Found",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_team_status("nonexistent-team")
    
    @pytest.mark.asyncio
    async def test_get_team_status_500_error(self, client):
        """Test handling of 500 error during status retrieval."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_team_status("test-team-123")
    
    @pytest.mark.asyncio
    async def test_get_team_status_timeout(self, client):
        """Test handling of timeout during status retrieval."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.TimeoutException):
                await client.get_team_status("test-team-123")


class TestGetSachstand:
    """Tests for get_sachstand method."""
    
    @pytest.mark.asyncio
    async def test_get_sachstand_success(self, client):
        """Test successful retrieval of sachstand."""
        mock_response_data = {
            "file_path": "/path/to/sachstand.jsonld",
            "content": {
                "@context": "https://schema.org",
                "@type": "ResearchReport",
                "name": "Sachstand: Test Topic",
                "hasPart": []
            }
        }
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_sachstand("test-team-123")
        
        assert result == mock_response_data
        assert "file_path" in result
        assert "content" in result
        assert result["content"]["@type"] == "ResearchReport"
        
        mock_client.get.assert_called_once_with(
            "http://localhost:8000/api/v1/sachstand/test-team-123"
        )
    
    @pytest.mark.asyncio
    async def test_get_sachstand_404_error(self, client):
        """Test handling of 404 error when sachstand not found."""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Not Found",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_sachstand("nonexistent-team")
    
    @pytest.mark.asyncio
    async def test_get_sachstand_500_error(self, client):
        """Test handling of 500 error during sachstand retrieval."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_sachstand("test-team-123")
    
    @pytest.mark.asyncio
    async def test_get_sachstand_timeout(self, client):
        """Test handling of timeout during sachstand retrieval."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.TimeoutException):
                await client.get_sachstand("test-team-123")
    
    @pytest.mark.asyncio
    async def test_get_sachstand_with_entities(self, client):
        """Test retrieval of sachstand with multiple entities."""
        mock_response_data = {
            "file_path": "/path/to/sachstand.jsonld",
            "content": {
                "@context": "https://schema.org",
                "@type": "ResearchReport",
                "name": "Sachstand: Test Topic",
                "hasPart": [
                    {
                        "@type": "Person",
                        "name": "John Doe",
                        "description": "Test person"
                    },
                    {
                        "@type": "Organization",
                        "name": "Test Org",
                        "description": "Test organization"
                    }
                ]
            }
        }
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_sachstand("test-team-123")
        
        assert len(result["content"]["hasPart"]) == 2
        assert result["content"]["hasPart"][0]["@type"] == "Person"
        assert result["content"]["hasPart"][1]["@type"] == "Organization"


class TestListTeams:
    """Tests for list_teams method."""
    
    @pytest.mark.asyncio
    async def test_list_teams_success(self, client):
        """Test successful retrieval of team list."""
        mock_response_data = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            },
            {
                "team_id": "team-2",
                "topic": "AI Ethics",
                "status": "pending",
                "created_at": "2025-10-16T11:00:00Z"
            },
            {
                "team_id": "team-3",
                "topic": "Renewable Energy",
                "status": "running",
                "created_at": "2025-10-16T12:00:00Z"
            }
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams()
        
        assert len(result) == 3
        assert result[0]["team_id"] == "team-1"
        assert result[1]["team_id"] == "team-2"
        assert result[2]["team_id"] == "team-3"
        
        mock_client.get.assert_called_once_with(
            "http://localhost:8000/api/v1/agent-teams",
            params={}
        )
    
    @pytest.mark.asyncio
    async def test_list_teams_with_topic_filter(self, client):
        """Test listing teams with topic filter (client-side filtering)."""
        mock_response_data = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            },
            {
                "team_id": "team-2",
                "topic": "AI Ethics",
                "status": "pending",
                "created_at": "2025-10-16T11:00:00Z"
            },
            {
                "team_id": "team-3",
                "topic": "Climate Policy",
                "status": "running",
                "created_at": "2025-10-16T12:00:00Z"
            }
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(topic_filter="climate")
        
        # Should return only teams with "climate" in topic (case-insensitive)
        assert len(result) == 2
        assert result[0]["team_id"] == "team-1"
        assert result[1]["team_id"] == "team-3"
        
        # Verify query parameter was passed (backend may or may not use it)
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["topic"] == "climate"
    
    @pytest.mark.asyncio
    async def test_list_teams_with_status_filter(self, client):
        """Test listing teams with status filter (client-side filtering)."""
        mock_response_data = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            },
            {
                "team_id": "team-2",
                "topic": "AI Ethics",
                "status": "pending",
                "created_at": "2025-10-16T11:00:00Z"
            },
            {
                "team_id": "team-3",
                "topic": "Renewable Energy",
                "status": "completed",
                "created_at": "2025-10-16T12:00:00Z"
            }
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(status_filter="completed")
        
        # Should return only completed teams
        assert len(result) == 2
        assert result[0]["status"] == "completed"
        assert result[1]["status"] == "completed"
        
        # Verify query parameter was passed
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_list_teams_with_combined_filters(self, client):
        """Test listing teams with both topic and status filters."""
        mock_response_data = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            },
            {
                "team_id": "team-2",
                "topic": "Climate Policy",
                "status": "pending",
                "created_at": "2025-10-16T11:00:00Z"
            },
            {
                "team_id": "team-3",
                "topic": "Climate Action",
                "status": "completed",
                "created_at": "2025-10-16T12:00:00Z"
            }
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(
                topic_filter="climate",
                status_filter="completed"
            )
        
        # Should return only completed teams with "climate" in topic
        assert len(result) == 2
        assert result[0]["team_id"] == "team-1"
        assert result[1]["team_id"] == "team-3"
        assert all(team["status"] == "completed" for team in result)
    
    @pytest.mark.asyncio
    async def test_list_teams_with_limit(self, client):
        """Test listing teams with limit parameter."""
        mock_response_data = [
            {"team_id": f"team-{i}", "topic": f"Topic {i}", "status": "completed"}
            for i in range(1, 11)
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(limit=5)
        
        # Should return only first 5 teams
        assert len(result) == 5
        assert result[0]["team_id"] == "team-1"
        assert result[4]["team_id"] == "team-5"
        
        # Verify limit parameter was passed
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["limit"] == 5
    
    @pytest.mark.asyncio
    async def test_list_teams_with_offset(self, client):
        """Test listing teams with offset parameter for pagination."""
        mock_response_data = [
            {"team_id": f"team-{i}", "topic": f"Topic {i}", "status": "completed"}
            for i in range(1, 11)
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(offset=3)
        
        # Should skip first 3 teams
        assert len(result) == 7
        assert result[0]["team_id"] == "team-4"
        
        # Verify offset parameter was passed
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["offset"] == 3
    
    @pytest.mark.asyncio
    async def test_list_teams_with_limit_and_offset(self, client):
        """Test listing teams with both limit and offset for pagination."""
        mock_response_data = [
            {"team_id": f"team-{i}", "topic": f"Topic {i}", "status": "completed"}
            for i in range(1, 21)
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(offset=5, limit=10)
        
        # Should skip first 5 and return next 10
        assert len(result) == 10
        assert result[0]["team_id"] == "team-6"
        assert result[9]["team_id"] == "team-15"
    
    @pytest.mark.asyncio
    async def test_list_teams_empty_result(self, client):
        """Test listing teams when no teams exist."""
        mock_response_data = []
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams()
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_list_teams_wrapped_response(self, client):
        """Test listing teams when backend returns wrapped response."""
        mock_response_data = {
            "teams": [
                {"team_id": "team-1", "topic": "Topic 1", "status": "completed"},
                {"team_id": "team-2", "topic": "Topic 2", "status": "pending"}
            ],
            "total": 2
        }
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams()
        
        # Should extract teams from wrapped response
        assert len(result) == 2
        assert result[0]["team_id"] == "team-1"
        assert result[1]["team_id"] == "team-2"
    
    @pytest.mark.asyncio
    async def test_list_teams_http_500_error(self, client):
        """Test handling of 500 error during team listing."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        def raise_status_error():
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=AsyncMock(),
                response=mock_response
            )
        
        mock_response.raise_for_status = raise_status_error
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await client.list_teams()
    
    @pytest.mark.asyncio
    async def test_list_teams_timeout(self, client):
        """Test handling of timeout during team listing."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.TimeoutException):
                await client.list_teams()
    
    @pytest.mark.asyncio
    async def test_list_teams_case_insensitive_topic_filter(self, client):
        """Test that topic filtering is case-insensitive."""
        mock_response_data = [
            {"team_id": "team-1", "topic": "CLIMATE CHANGE", "status": "completed"},
            {"team_id": "team-2", "topic": "AI Ethics", "status": "pending"},
            {"team_id": "team-3", "topic": "climate policy", "status": "running"}
        ]
        
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_response_data
        mock_response.raise_for_status = lambda: None
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch("mcp_server.fastapi_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.list_teams(topic_filter="Climate")
        
        # Should match both "CLIMATE CHANGE" and "climate policy"
        assert len(result) == 2
        assert result[0]["team_id"] == "team-1"
        assert result[1]["team_id"] == "team-3"
