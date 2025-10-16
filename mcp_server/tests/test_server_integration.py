"""
Integration tests for LibreChatMCPServer.

Tests cover:
- Each tool handler with mocked dependencies
- Error handling for each tool
- Parameter validation
- Integration between server components
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from mcp_server.server import LibreChatMCPServer
from mcp_server.fastapi_client import FastAPIClient


@pytest.fixture
def mock_fastapi_client():
    """Create a mock FastAPIClient for testing."""
    client = AsyncMock(spec=FastAPIClient)
    return client


@pytest.fixture
def server(mock_fastapi_client):
    """Create a LibreChatMCPServer instance with mocked client."""
    with patch("mcp_server.server.FastAPIClient", return_value=mock_fastapi_client):
        server = LibreChatMCPServer(api_base_url="http://localhost:8000")
        server.fastapi_client = mock_fastapi_client
        return server


class TestSpawnAgentTeam:
    """Tests for spawn_agent_team tool handler."""
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_success(self, server, mock_fastapi_client):
        """Test successful agent team spawning."""
        # Mock backend response
        mock_fastapi_client.create_team.return_value = {
            "team_id": "test-team-123",
            "status": "pending",
            "created_at": "2025-10-16T10:00:00Z"
        }
        
        result = await server.spawn_agent_team(
            topic="Climate Change",
            goals=["Goal 1", "Goal 2"],
            interaction_limit=50
        )
        
        # Verify response structure
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "Action"
        assert result["object"]["identifier"] == "test-team-123"
        assert result["object"]["name"] == "Climate Change"
        assert result["object"]["status"] == "pending"
        
        # Verify client was called correctly
        mock_fastapi_client.create_team.assert_called_once_with(
            topic="Climate Change",
            goals=["Goal 1", "Goal 2"],
            interaction_limit=50
        )
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_with_default_goals(self, server, mock_fastapi_client):
        """Test spawning with default empty goals list."""
        mock_fastapi_client.create_team.return_value = {
            "team_id": "test-team-456",
            "status": "pending",
            "created_at": "2025-10-16T10:00:00Z"
        }
        
        result = await server.spawn_agent_team(
            topic="AI Ethics",
            interaction_limit=100
        )
        
        # Should use empty list for goals
        mock_fastapi_client.create_team.assert_called_once()
        call_args = mock_fastapi_client.create_team.call_args
        assert call_args[1]["goals"] == []
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_empty_topic(self, server, mock_fastapi_client):
        """Test error handling for empty topic."""
        result = await server.spawn_agent_team(
            topic="",
            goals=["Goal 1"]
        )
        
        # Should return error response
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "Topic parameter is required" in result["error"]["message"]
        
        # Should not call backend
        mock_fastapi_client.create_team.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_whitespace_topic(self, server, mock_fastapi_client):
        """Test error handling for whitespace-only topic."""
        result = await server.spawn_agent_team(
            topic="   ",
            goals=["Goal 1"]
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        mock_fastapi_client.create_team.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_invalid_interaction_limit_low(self, server, mock_fastapi_client):
        """Test error handling for interaction_limit < 1."""
        result = await server.spawn_agent_team(
            topic="Test Topic",
            interaction_limit=0
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "interaction_limit must be between 1 and 1000" in result["error"]["message"]
        mock_fastapi_client.create_team.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_invalid_interaction_limit_high(self, server, mock_fastapi_client):
        """Test error handling for interaction_limit > 1000."""
        result = await server.spawn_agent_team(
            topic="Test Topic",
            interaction_limit=1001
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "interaction_limit must be between 1 and 1000" in result["error"]["message"]
        mock_fastapi_client.create_team.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_http_error(self, server, mock_fastapi_client):
        """Test error handling for HTTP errors from backend."""
        mock_fastapi_client.create_team.side_effect = httpx.HTTPError("Connection failed")
        
        result = await server.spawn_agent_team(
            topic="Test Topic",
            goals=["Goal 1"]
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "BACKEND_ERROR"
        assert "Failed to spawn agent team" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_spawn_agent_team_unexpected_error(self, server, mock_fastapi_client):
        """Test error handling for unexpected exceptions."""
        mock_fastapi_client.create_team.side_effect = ValueError("Unexpected error")
        
        result = await server.spawn_agent_team(
            topic="Test Topic",
            goals=["Goal 1"]
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INTERNAL_ERROR"
        assert "Unexpected error" in result["error"]["message"]


class TestGetExecutionStatus:
    """Tests for get_execution_status tool handler."""
    
    @pytest.mark.asyncio
    async def test_get_execution_status_pending(self, server, mock_fastapi_client):
        """Test getting status for pending execution."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-123",
            "topic": "Climate Change",
            "status": "pending",
            "created_at": "2025-10-16T10:00:00Z"
        }
        
        result = await server.get_execution_status(execution_id="test-team-123")
        
        assert result["@type"] == "ResearchReport"
        assert result["identifier"] == "test-team-123"
        assert result["name"] == "Climate Change"
        assert result["status"] == "pending"
        assert "numberOfEntities" not in result
        assert "duration" not in result
        
        mock_fastapi_client.get_team_status.assert_called_once_with("test-team-123")
    
    @pytest.mark.asyncio
    async def test_get_execution_status_running(self, server, mock_fastapi_client):
        """Test getting status for running execution."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-456",
            "topic": "AI Ethics",
            "status": "running",
            "created_at": "2025-10-16T10:00:00Z",
            "updated_at": "2025-10-16T10:02:00Z"
        }
        
        result = await server.get_execution_status(execution_id="test-team-456")
        
        assert result["status"] == "running"
        assert result["dateModified"] == "2025-10-16T10:02:00Z"
        assert "numberOfEntities" not in result
    
    @pytest.mark.asyncio
    async def test_get_execution_status_completed(self, server, mock_fastapi_client):
        """Test getting status for completed execution with entities."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-789",
            "topic": "Renewable Energy",
            "status": "completed",
            "created_at": "2025-10-16T10:00:00Z",
            "updated_at": "2025-10-16T10:05:23Z",
            "sachstand": {
                "@type": "ResearchReport",
                "hasPart": [
                    {"@type": "Person", "name": "Person 1"},
                    {"@type": "Organization", "name": "Org 1"},
                    {"@type": "Event", "name": "Event 1"}
                ]
            }
        }
        
        result = await server.get_execution_status(execution_id="test-team-789")
        
        assert result["status"] == "completed"
        assert result["numberOfEntities"] == 3
        assert result["duration"] == "PT5M23S"
    
    @pytest.mark.asyncio
    async def test_get_execution_status_failed(self, server, mock_fastapi_client):
        """Test getting status for failed execution."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-999",
            "topic": "Failed Topic",
            "status": "failed",
            "created_at": "2025-10-16T10:00:00Z",
            "updated_at": "2025-10-16T10:01:00Z"
        }
        
        result = await server.get_execution_status(execution_id="test-team-999")
        
        assert result["status"] == "failed"
        assert "numberOfEntities" not in result
    
    @pytest.mark.asyncio
    async def test_get_execution_status_empty_execution_id(self, server, mock_fastapi_client):
        """Test error handling for empty execution_id."""
        result = await server.get_execution_status(execution_id="")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "execution_id parameter is required" in result["error"]["message"]
        mock_fastapi_client.get_team_status.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_execution_status_whitespace_execution_id(self, server, mock_fastapi_client):
        """Test error handling for whitespace-only execution_id."""
        result = await server.get_execution_status(execution_id="   ")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        mock_fastapi_client.get_team_status.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_execution_status_not_found(self, server, mock_fastapi_client):
        """Test error handling for execution not found (404)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        mock_fastapi_client.get_team_status.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=mock_response
        )
        
        result = await server.get_execution_status(execution_id="nonexistent")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_FOUND"
        assert "nonexistent" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_execution_status_http_error(self, server, mock_fastapi_client):
        """Test error handling for HTTP errors."""
        mock_fastapi_client.get_team_status.side_effect = httpx.HTTPError("Connection failed")
        
        result = await server.get_execution_status(execution_id="test-team-123")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "BACKEND_ERROR"
        assert "Failed to get execution status" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_execution_status_unexpected_error(self, server, mock_fastapi_client):
        """Test error handling for unexpected exceptions."""
        mock_fastapi_client.get_team_status.side_effect = ValueError("Unexpected error")
        
        result = await server.get_execution_status(execution_id="test-team-123")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INTERNAL_ERROR"


class TestGetExecutionResults:
    """Tests for get_execution_results tool handler."""
    
    @pytest.mark.asyncio
    async def test_get_execution_results_success(self, server, mock_fastapi_client):
        """Test successful retrieval of execution results."""
        # Mock status check
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-123",
            "status": "completed"
        }
        
        # Mock sachstand retrieval
        sachstand = {
            "@context": "https://schema.org",
            "@type": "ResearchReport",
            "name": "Sachstand: Climate Change",
            "hasPart": [
                {"@type": "Person", "name": "John Doe"}
            ]
        }
        mock_fastapi_client.get_sachstand.return_value = {
            "file_path": "/path/to/sachstand.jsonld",
            "content": sachstand
        }
        
        result = await server.get_execution_results(execution_id="test-team-123")
        
        # Should return the sachstand content
        assert result == sachstand
        assert result["@type"] == "ResearchReport"
        assert result["name"] == "Sachstand: Climate Change"
        
        mock_fastapi_client.get_team_status.assert_called_once_with("test-team-123")
        mock_fastapi_client.get_sachstand.assert_called_once_with("test-team-123")
    
    @pytest.mark.asyncio
    async def test_get_execution_results_not_completed(self, server, mock_fastapi_client):
        """Test error when execution is not completed."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-456",
            "status": "running"
        }
        
        result = await server.get_execution_results(execution_id="test-team-456")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_COMPLETED"
        assert "not completed yet" in result["error"]["message"]
        assert "running" in result["error"]["message"]
        
        # Should not call get_sachstand
        mock_fastapi_client.get_sachstand.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_execution_results_pending(self, server, mock_fastapi_client):
        """Test error when execution is still pending."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-789",
            "status": "pending"
        }
        
        result = await server.get_execution_results(execution_id="test-team-789")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_COMPLETED"
        assert "pending" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_execution_results_no_content(self, server, mock_fastapi_client):
        """Test error when sachstand has no content."""
        mock_fastapi_client.get_team_status.return_value = {
            "team_id": "test-team-111",
            "status": "completed"
        }
        
        mock_fastapi_client.get_sachstand.return_value = {
            "file_path": "/path/to/sachstand.jsonld",
            "content": None
        }
        
        result = await server.get_execution_results(execution_id="test-team-111")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "RESULTS_NOT_AVAILABLE"
        assert "results are not available" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_execution_results_empty_execution_id(self, server, mock_fastapi_client):
        """Test error handling for empty execution_id."""
        result = await server.get_execution_results(execution_id="")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        mock_fastapi_client.get_team_status.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_execution_results_not_found(self, server, mock_fastapi_client):
        """Test error handling for execution not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        mock_fastapi_client.get_team_status.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=mock_response
        )
        
        result = await server.get_execution_results(execution_id="nonexistent")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_execution_results_http_error(self, server, mock_fastapi_client):
        """Test error handling for HTTP errors."""
        mock_fastapi_client.get_team_status.side_effect = httpx.HTTPError("Connection failed")
        
        result = await server.get_execution_results(execution_id="test-team-123")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "BACKEND_ERROR"
    
    @pytest.mark.asyncio
    async def test_get_execution_results_unexpected_error(self, server, mock_fastapi_client):
        """Test error handling for unexpected exceptions."""
        mock_fastapi_client.get_team_status.side_effect = ValueError("Unexpected error")
        
        result = await server.get_execution_results(execution_id="test-team-123")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INTERNAL_ERROR"


class TestListExecutions:
    """Tests for list_executions tool handler."""
    
    @pytest.mark.asyncio
    async def test_list_executions_success(self, server, mock_fastapi_client):
        """Test successful listing of executions."""
        mock_teams = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            },
            {
                "team_id": "team-2",
                "topic": "AI Ethics",
                "status": "running",
                "created_at": "2025-10-16T11:00:00Z"
            }
        ]
        
        mock_fastapi_client.list_teams.return_value = mock_teams
        
        result = await server.list_executions()
        
        assert result["@type"] == "ItemList"
        assert result["numberOfItems"] == 2
        assert len(result["itemListElement"]) == 2
        
        mock_fastapi_client.list_teams.assert_called_once_with(
            topic_filter=None,
            status_filter=None,
            limit=10,
            offset=0
        )
    
    @pytest.mark.asyncio
    async def test_list_executions_with_filters(self, server, mock_fastapi_client):
        """Test listing with topic and status filters."""
        mock_teams = [
            {
                "team_id": "team-1",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            }
        ]
        
        mock_fastapi_client.list_teams.return_value = mock_teams
        
        result = await server.list_executions(
            topic_filter="climate",
            status_filter="completed"
        )
        
        assert result["@type"] == "ItemList"
        assert result["numberOfItems"] == 1
        
        mock_fastapi_client.list_teams.assert_called_once_with(
            topic_filter="climate",
            status_filter="completed",
            limit=10,
            offset=0
        )
    
    @pytest.mark.asyncio
    async def test_list_executions_with_pagination(self, server, mock_fastapi_client):
        """Test listing with limit and offset."""
        mock_teams = [
            {"team_id": f"team-{i}", "topic": f"Topic {i}", "status": "completed"}
            for i in range(6, 11)
        ]
        
        mock_fastapi_client.list_teams.return_value = mock_teams
        
        result = await server.list_executions(limit=5, offset=5)
        
        assert result["numberOfItems"] == 5
        
        mock_fastapi_client.list_teams.assert_called_once_with(
            topic_filter=None,
            status_filter=None,
            limit=5,
            offset=5
        )
    
    @pytest.mark.asyncio
    async def test_list_executions_empty_result(self, server, mock_fastapi_client):
        """Test listing when no executions exist."""
        mock_fastapi_client.list_teams.return_value = []
        
        result = await server.list_executions()
        
        assert result["@type"] == "ItemList"
        assert result["numberOfItems"] == 0
        assert result["itemListElement"] == []
    
    @pytest.mark.asyncio
    async def test_list_executions_invalid_limit_low(self, server, mock_fastapi_client):
        """Test error handling for limit < 1."""
        result = await server.list_executions(limit=0)
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "limit must be between 1 and 100" in result["error"]["message"]
        mock_fastapi_client.list_teams.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_executions_invalid_limit_high(self, server, mock_fastapi_client):
        """Test error handling for limit > 100."""
        result = await server.list_executions(limit=101)
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "limit must be between 1 and 100" in result["error"]["message"]
        mock_fastapi_client.list_teams.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_executions_invalid_offset(self, server, mock_fastapi_client):
        """Test error handling for negative offset."""
        result = await server.list_executions(offset=-1)
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "offset must be non-negative" in result["error"]["message"]
        mock_fastapi_client.list_teams.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_executions_invalid_status_filter(self, server, mock_fastapi_client):
        """Test error handling for invalid status_filter."""
        result = await server.list_executions(status_filter="invalid_status")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        assert "Invalid status_filter" in result["error"]["message"]
        assert "pending, running, completed, failed" in result["error"]["message"]
        mock_fastapi_client.list_teams.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_executions_valid_status_filters(self, server, mock_fastapi_client):
        """Test that all valid status filters are accepted."""
        valid_statuses = ["pending", "running", "completed", "failed"]
        
        for status in valid_statuses:
            mock_fastapi_client.list_teams.return_value = []
            
            result = await server.list_executions(status_filter=status)
            
            # Should not return error
            assert result["@type"] == "ItemList"
            
            # Verify correct status was passed
            call_args = mock_fastapi_client.list_teams.call_args
            assert call_args[1]["status_filter"] == status
    
    @pytest.mark.asyncio
    async def test_list_executions_http_error(self, server, mock_fastapi_client):
        """Test error handling for HTTP errors."""
        mock_fastapi_client.list_teams.side_effect = httpx.HTTPError("Connection failed")
        
        result = await server.list_executions()
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "BACKEND_ERROR"
        assert "Failed to list executions" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_list_executions_unexpected_error(self, server, mock_fastapi_client):
        """Test error handling for unexpected exceptions."""
        mock_fastapi_client.list_teams.side_effect = ValueError("Unexpected error")
        
        result = await server.list_executions()
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INTERNAL_ERROR"


class TestServerInitialization:
    """Tests for LibreChatMCPServer initialization."""
    
    def test_server_initialization(self):
        """Test that server initializes correctly."""
        with patch("mcp_server.server.FastAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            server = LibreChatMCPServer(api_base_url="http://localhost:8000")
            
            # Verify FastAPIClient was created with correct URL and default timeout
            mock_client_class.assert_called_once_with("http://localhost:8000", timeout=30.0)
            
            # Verify server has fastapi_client attribute
            assert server.fastapi_client == mock_client
            
            # Verify server instance was created
            assert server.server is not None
            assert server.server.name == "librechat-osint-mcp"
    
    def test_server_initialization_with_different_url(self):
        """Test server initialization with different base URL."""
        with patch("mcp_server.server.FastAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            server = LibreChatMCPServer(api_base_url="http://example.com:9000")
            
            mock_client_class.assert_called_once_with("http://example.com:9000", timeout=30.0)
    
    def test_server_initialization_with_custom_timeout(self):
        """Test server initialization with custom timeout."""
        with patch("mcp_server.server.FastAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            server = LibreChatMCPServer(api_base_url="http://localhost:8000", timeout=60.0)
            
            mock_client_class.assert_called_once_with("http://localhost:8000", timeout=60.0)


class TestParameterValidation:
    """Tests for parameter validation across all tools."""
    
    @pytest.mark.asyncio
    async def test_spawn_validates_topic_type(self, server, mock_fastapi_client):
        """Test that spawn_agent_team validates topic parameter."""
        # Empty string
        result = await server.spawn_agent_team(topic="")
        assert result["@type"] == "ErrorResponse"
        
        # Whitespace only
        result = await server.spawn_agent_team(topic="   ")
        assert result["@type"] == "ErrorResponse"
    
    @pytest.mark.asyncio
    async def test_spawn_validates_interaction_limit_range(self, server, mock_fastapi_client):
        """Test that spawn_agent_team validates interaction_limit range."""
        # Too low
        result = await server.spawn_agent_team(topic="Test", interaction_limit=0)
        assert result["@type"] == "ErrorResponse"
        
        # Too high
        result = await server.spawn_agent_team(topic="Test", interaction_limit=1001)
        assert result["@type"] == "ErrorResponse"
        
        # Valid boundaries
        mock_fastapi_client.create_team.return_value = {
            "team_id": "test", "status": "pending", "created_at": "2025-10-16T10:00:00Z"
        }
        
        result = await server.spawn_agent_team(topic="Test", interaction_limit=1)
        assert result["@type"] == "Action"
        
        result = await server.spawn_agent_team(topic="Test", interaction_limit=1000)
        assert result["@type"] == "Action"
    
    @pytest.mark.asyncio
    async def test_status_validates_execution_id(self, server, mock_fastapi_client):
        """Test that get_execution_status validates execution_id."""
        # Empty string
        result = await server.get_execution_status(execution_id="")
        assert result["@type"] == "ErrorResponse"
        
        # Whitespace only
        result = await server.get_execution_status(execution_id="   ")
        assert result["@type"] == "ErrorResponse"
    
    @pytest.mark.asyncio
    async def test_results_validates_execution_id(self, server, mock_fastapi_client):
        """Test that get_execution_results validates execution_id."""
        # Empty string
        result = await server.get_execution_results(execution_id="")
        assert result["@type"] == "ErrorResponse"
        
        # Whitespace only
        result = await server.get_execution_results(execution_id="   ")
        assert result["@type"] == "ErrorResponse"
    
    @pytest.mark.asyncio
    async def test_list_validates_limit_range(self, server, mock_fastapi_client):
        """Test that list_executions validates limit range."""
        # Too low
        result = await server.list_executions(limit=0)
        assert result["@type"] == "ErrorResponse"
        
        # Too high
        result = await server.list_executions(limit=101)
        assert result["@type"] == "ErrorResponse"
        
        # Valid boundaries
        mock_fastapi_client.list_teams.return_value = []
        
        result = await server.list_executions(limit=1)
        assert result["@type"] == "ItemList"
        
        result = await server.list_executions(limit=100)
        assert result["@type"] == "ItemList"
    
    @pytest.mark.asyncio
    async def test_list_validates_offset(self, server, mock_fastapi_client):
        """Test that list_executions validates offset."""
        # Negative offset
        result = await server.list_executions(offset=-1)
        assert result["@type"] == "ErrorResponse"
        
        # Valid offset
        mock_fastapi_client.list_teams.return_value = []
        result = await server.list_executions(offset=0)
        assert result["@type"] == "ItemList"
    
    @pytest.mark.asyncio
    async def test_list_validates_status_filter(self, server, mock_fastapi_client):
        """Test that list_executions validates status_filter."""
        # Invalid status
        result = await server.list_executions(status_filter="invalid")
        assert result["@type"] == "ErrorResponse"
        
        # Valid statuses
        mock_fastapi_client.list_teams.return_value = []
        for status in ["pending", "running", "completed", "failed"]:
            result = await server.list_executions(status_filter=status)
            assert result["@type"] == "ItemList"
