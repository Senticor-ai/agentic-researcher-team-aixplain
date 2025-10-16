#!/usr/bin/env python3
"""End-to-end integration tests for the MCP server.

These tests require the FastAPI backend to be running.
They test the full workflow with real HTTP requests.

Usage:
    # Start the FastAPI backend first
    ./start-backend.sh
    
    # Run the tests
    pytest mcp_server/tests/test_e2e_integration.py -v
    
    # Or run with markers
    pytest mcp_server/tests/test_e2e_integration.py -v -m e2e
"""

import asyncio
import json
import os
import pytest
import httpx
from typing import Dict, Any

from mcp_server.fastapi_client import FastAPIClient
from mcp_server.server import LibreChatMCPServer
from mcp_server.config import Config


# Mark all tests in this module as e2e tests
pytestmark = pytest.mark.e2e


@pytest.fixture
def backend_url() -> str:
    """Get backend URL from environment or use default."""
    return os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")


@pytest.fixture
async def check_backend_available(backend_url: str):
    """Check if the FastAPI backend is available before running tests."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{backend_url}/health", timeout=5.0)
            if response.status_code != 200:
                pytest.skip(f"Backend not healthy: {response.status_code}")
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            pytest.skip(f"Backend not available at {backend_url}: {e}")


@pytest.fixture
def fastapi_client(backend_url: str) -> FastAPIClient:
    """Create a FastAPIClient instance for testing."""
    return FastAPIClient(base_url=backend_url, timeout=60.0)


@pytest.fixture
def mcp_server(backend_url: str) -> LibreChatMCPServer:
    """Create a LibreChatMCPServer instance for testing."""
    return LibreChatMCPServer(api_base_url=backend_url, timeout=60.0)


class TestFullWorkflow:
    """Test the complete workflow: spawn → status → results."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_success(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test the complete workflow with a real backend.
        
        This test:
        1. Spawns an agent team
        2. Polls for completion
        3. Retrieves results
        4. Validates JSON-LD format
        """
        # Step 1: Spawn agent team
        spawn_result = await mcp_server.spawn_agent_team(
            topic="Test E2E Integration",
            goals=["Test goal 1", "Test goal 2"],
            interaction_limit=20  # Keep it short for testing
        )
        
        # Validate spawn response
        assert spawn_result["@context"] == "https://schema.org"
        assert spawn_result["@type"] == "Action"
        assert "object" in spawn_result
        assert "identifier" in spawn_result["object"]
        
        team_id = spawn_result["object"]["identifier"]
        assert team_id is not None
        assert len(team_id) > 0
        
        print(f"\n✓ Spawned team: {team_id}")
        
        # Step 2: Poll for completion
        max_wait = 180  # 3 minutes max
        poll_interval = 5
        elapsed = 0
        final_status = None
        
        while elapsed < max_wait:
            status_result = await mcp_server.get_execution_status(execution_id=team_id)
            
            # Validate status response format
            assert status_result["@context"] == "https://schema.org"
            assert status_result["@type"] == "ResearchReport"
            assert status_result["identifier"] == team_id
            assert "status" in status_result
            
            status = status_result["status"]
            print(f"  Status: {status} (elapsed: {elapsed}s)")
            
            if status == "completed":
                final_status = status_result
                break
            elif status == "failed":
                pytest.fail(f"Execution failed: {status_result}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        if final_status is None:
            pytest.fail(f"Execution did not complete within {max_wait} seconds")
        
        # Validate completed status includes entity count
        assert "numberOfEntities" in final_status
        assert isinstance(final_status["numberOfEntities"], int)
        assert final_status["numberOfEntities"] >= 0
        
        print(f"✓ Completed with {final_status['numberOfEntities']} entities")
        
        # Step 3: Retrieve results
        results = await mcp_server.get_execution_results(execution_id=team_id)
        
        # Validate JSON-LD format
        assert results["@context"] == "https://schema.org"
        assert results["@type"] == "ResearchReport"
        assert "name" in results
        assert "hasPart" in results
        assert isinstance(results["hasPart"], list)
        
        # Validate entities
        entities = results["hasPart"]
        assert len(entities) == final_status["numberOfEntities"]
        
        for entity in entities:
            assert "@type" in entity
            assert "name" in entity
            assert "description" in entity
            assert "sources" in entity
            assert isinstance(entity["sources"], list)
        
        print(f"✓ Retrieved {len(entities)} entities")
        print(f"✓ Full workflow completed successfully")


class TestSpawnAgentTeam:
    """Test spawning agent teams with various configurations."""
    
    @pytest.mark.asyncio
    async def test_spawn_with_minimal_params(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test spawning with only required parameters."""
        result = await mcp_server.spawn_agent_team(
            topic="Minimal Test Topic"
        )
        
        assert result["@type"] == "Action"
        assert result["object"]["name"] == "Minimal Test Topic"
        assert result["object"]["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_spawn_with_all_params(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test spawning with all parameters."""
        result = await mcp_server.spawn_agent_team(
            topic="Full Params Test",
            goals=["Goal 1", "Goal 2", "Goal 3"],
            interaction_limit=100
        )
        
        assert result["@type"] == "Action"
        assert result["object"]["name"] == "Full Params Test"
    
    @pytest.mark.asyncio
    async def test_spawn_validation_errors(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test parameter validation errors."""
        # Empty topic
        result = await mcp_server.spawn_agent_team(topic="")
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        
        # Invalid interaction_limit
        result = await mcp_server.spawn_agent_team(
            topic="Test",
            interaction_limit=0
        )
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"


class TestGetExecutionStatus:
    """Test getting execution status."""
    
    @pytest.mark.asyncio
    async def test_get_status_for_existing_execution(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test getting status for an existing execution."""
        # First spawn a team
        spawn_result = await mcp_server.spawn_agent_team(
            topic="Status Test Topic"
        )
        team_id = spawn_result["object"]["identifier"]
        
        # Get status
        status_result = await mcp_server.get_execution_status(execution_id=team_id)
        
        assert status_result["@type"] == "ResearchReport"
        assert status_result["identifier"] == team_id
        assert status_result["status"] in ["pending", "running", "completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_get_status_not_found(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test getting status for non-existent execution."""
        result = await mcp_server.get_execution_status(
            execution_id="nonexistent-team-id-12345"
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_status_validation_errors(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test parameter validation errors."""
        result = await mcp_server.get_execution_status(execution_id="")
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"


class TestGetExecutionResults:
    """Test retrieving execution results."""
    
    @pytest.mark.asyncio
    async def test_get_results_not_completed(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test getting results for execution that's not completed."""
        # Spawn a team
        spawn_result = await mcp_server.spawn_agent_team(
            topic="Results Test Topic"
        )
        team_id = spawn_result["object"]["identifier"]
        
        # Try to get results immediately (should not be completed yet)
        result = await mcp_server.get_execution_results(execution_id=team_id)
        
        # Should return error if not completed
        # (unless it completed extremely fast)
        if result.get("@type") == "ErrorResponse":
            assert result["error"]["code"] == "EXECUTION_NOT_COMPLETED"
    
    @pytest.mark.asyncio
    async def test_get_results_not_found(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test getting results for non-existent execution."""
        result = await mcp_server.get_execution_results(
            execution_id="nonexistent-team-id-67890"
        )
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "EXECUTION_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_results_validation_errors(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test parameter validation errors."""
        result = await mcp_server.get_execution_results(execution_id="")
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"


class TestListExecutions:
    """Test listing executions."""
    
    @pytest.mark.asyncio
    async def test_list_all_executions(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test listing all executions."""
        result = await mcp_server.list_executions()
        
        assert result["@type"] == "ItemList"
        assert "numberOfItems" in result
        assert "itemListElement" in result
        assert isinstance(result["itemListElement"], list)
        
        # Validate structure of items
        for item in result["itemListElement"]:
            assert item["@type"] == "ListItem"
            assert "position" in item
            assert "item" in item
            assert item["item"]["@type"] == "ResearchReport"
    
    @pytest.mark.asyncio
    async def test_list_with_topic_filter(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test listing with topic filter."""
        # Spawn a team with unique topic
        unique_topic = "UniqueFilterTest123"
        spawn_result = await mcp_server.spawn_agent_team(topic=unique_topic)
        
        # List with filter
        result = await mcp_server.list_executions(topic_filter=unique_topic)
        
        assert result["@type"] == "ItemList"
        assert result["numberOfItems"] >= 1
        
        # Verify filtered results contain our topic
        found = False
        for item in result["itemListElement"]:
            if unique_topic in item["item"]["name"]:
                found = True
                break
        assert found, f"Topic '{unique_topic}' not found in filtered results"
    
    @pytest.mark.asyncio
    async def test_list_with_status_filter(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test listing with status filter."""
        result = await mcp_server.list_executions(status_filter="completed")
        
        assert result["@type"] == "ItemList"
        
        # Verify all results have completed status
        for item in result["itemListElement"]:
            assert item["item"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_list_with_pagination(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test listing with pagination."""
        # Get first page
        page1 = await mcp_server.list_executions(limit=5, offset=0)
        assert page1["@type"] == "ItemList"
        assert len(page1["itemListElement"]) <= 5
        
        # Get second page
        page2 = await mcp_server.list_executions(limit=5, offset=5)
        assert page2["@type"] == "ItemList"
        
        # Pages should be different (if there are enough items)
        if page1["numberOfItems"] > 5:
            page1_ids = {item["item"]["identifier"] for item in page1["itemListElement"]}
            page2_ids = {item["item"]["identifier"] for item in page2["itemListElement"]}
            assert page1_ids != page2_ids
    
    @pytest.mark.asyncio
    async def test_list_validation_errors(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test parameter validation errors."""
        # Invalid limit
        result = await mcp_server.list_executions(limit=0)
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        
        # Invalid offset
        result = await mcp_server.list_executions(offset=-1)
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"
        
        # Invalid status filter
        result = await mcp_server.list_executions(status_filter="invalid")
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "INVALID_PARAMETER"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_backend_unavailable(self):
        """Test behavior when backend is unavailable."""
        # Create server pointing to non-existent backend
        server = LibreChatMCPServer(
            api_base_url="http://localhost:9999",
            timeout=5.0
        )
        
        result = await server.spawn_agent_team(topic="Test")
        
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] == "BACKEND_ERROR"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling."""
        # Create server with very short timeout
        server = LibreChatMCPServer(
            api_base_url="http://localhost:8000",
            timeout=0.001  # 1ms timeout
        )
        
        result = await server.spawn_agent_team(topic="Test")
        
        # Should get timeout error
        assert result["@type"] == "ErrorResponse"
        assert result["error"]["code"] in ["BACKEND_ERROR", "INTERNAL_ERROR"]


class TestJSONLDFormat:
    """Test JSON-LD format compliance."""
    
    @pytest.mark.asyncio
    async def test_spawn_response_jsonld(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test that spawn response follows JSON-LD format."""
        result = await mcp_server.spawn_agent_team(topic="JSON-LD Test")
        
        # Required JSON-LD fields
        assert "@context" in result
        assert result["@context"] == "https://schema.org"
        assert "@type" in result
        
        # Validate nested objects
        assert "@type" in result["object"]
        assert result["object"]["@type"] == "ResearchReport"
    
    @pytest.mark.asyncio
    async def test_status_response_jsonld(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test that status response follows JSON-LD format."""
        # Spawn a team first
        spawn_result = await mcp_server.spawn_agent_team(topic="Status JSON-LD Test")
        team_id = spawn_result["object"]["identifier"]
        
        # Get status
        result = await mcp_server.get_execution_status(execution_id=team_id)
        
        assert "@context" in result
        assert result["@context"] == "https://schema.org"
        assert "@type" in result
        assert result["@type"] == "ResearchReport"
    
    @pytest.mark.asyncio
    async def test_list_response_jsonld(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test that list response follows JSON-LD format."""
        result = await mcp_server.list_executions()
        
        assert "@context" in result
        assert result["@context"] == "https://schema.org"
        assert "@type" in result
        assert result["@type"] == "ItemList"
        
        # Validate list items
        for item in result["itemListElement"]:
            assert "@type" in item
            assert item["@type"] == "ListItem"
            assert "@type" in item["item"]
    
    @pytest.mark.asyncio
    async def test_error_response_jsonld(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test that error responses follow JSON-LD format."""
        result = await mcp_server.spawn_agent_team(topic="")
        
        assert "@context" in result
        assert result["@context"] == "https://schema.org"
        assert "@type" in result
        assert result["@type"] == "ErrorResponse"
        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]


class TestConcurrentRequests:
    """Test handling of concurrent requests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_spawns(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test spawning multiple teams concurrently."""
        topics = [f"Concurrent Test {i}" for i in range(3)]
        
        # Spawn teams concurrently
        tasks = [
            mcp_server.spawn_agent_team(topic=topic, interaction_limit=10)
            for topic in topics
        ]
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(results) == 3
        for result in results:
            assert result["@type"] == "Action"
            assert "identifier" in result["object"]
        
        # Verify unique team IDs
        team_ids = [r["object"]["identifier"] for r in results]
        assert len(set(team_ids)) == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_status_checks(
        self,
        check_backend_available,
        mcp_server: LibreChatMCPServer
    ):
        """Test checking status of multiple teams concurrently."""
        # Spawn a few teams first
        spawn_tasks = [
            mcp_server.spawn_agent_team(topic=f"Status Check {i}", interaction_limit=10)
            for i in range(3)
        ]
        spawn_results = await asyncio.gather(*spawn_tasks)
        team_ids = [r["object"]["identifier"] for r in spawn_results]
        
        # Check status concurrently
        status_tasks = [
            mcp_server.get_execution_status(execution_id=team_id)
            for team_id in team_ids
        ]
        status_results = await asyncio.gather(*status_tasks)
        
        # Verify all succeeded
        assert len(status_results) == 3
        for result in status_results:
            assert result["@type"] == "ResearchReport"
            assert "status" in result


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
