"""
Unit tests for JSON-LD response formatters.

Tests cover:
- Each formatter with sample data
- JSON-LD structure validation
- Required fields validation
- Error response formatting
"""
import pytest
from datetime import datetime, timezone

from mcp_server.formatters import (
    format_spawn_response,
    format_status_response,
    format_list_response,
    format_results_response,
    format_error_response,
    _format_iso8601_duration
)


class TestFormatSpawnResponse:
    """Tests for format_spawn_response function."""
    
    def test_format_spawn_response_basic(self):
        """Test basic spawn response formatting."""
        result = format_spawn_response(
            team_id="test-team-123",
            topic="Climate Change",
            created_at="2025-10-16T10:00:00Z"
        )
        
        # Validate JSON-LD structure
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "Action"
        assert result["actionStatus"] == "PotentialActionStatus"
        
        # Validate object structure
        assert result["object"]["@type"] == "ResearchReport"
        assert result["object"]["identifier"] == "test-team-123"
        assert result["object"]["name"] == "Climate Change"
        assert result["object"]["dateCreated"] == "2025-10-16T10:00:00Z"
        assert result["object"]["status"] == "pending"
        
        # Validate result message
        assert "message" in result["result"]
        assert "spawned successfully" in result["result"]["message"]
    
    def test_format_spawn_response_with_custom_status(self):
        """Test spawn response with custom status."""
        result = format_spawn_response(
            team_id="test-team-456",
            topic="AI Ethics",
            created_at="2025-10-16T11:00:00Z",
            status="running"
        )
        
        assert result["object"]["status"] == "running"
        assert result["object"]["identifier"] == "test-team-456"
    
    def test_format_spawn_response_required_fields(self):
        """Test that all required JSON-LD fields are present."""
        result = format_spawn_response(
            team_id="test-team-789",
            topic="Renewable Energy",
            created_at="2025-10-16T12:00:00Z"
        )
        
        # Check all required top-level fields
        required_fields = ["@context", "@type", "actionStatus", "object", "result"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check all required object fields
        required_object_fields = ["@type", "identifier", "name", "dateCreated", "status"]
        for field in required_object_fields:
            assert field in result["object"], f"Missing required object field: {field}"


class TestFormatStatusResponse:
    """Tests for format_status_response function."""
    
    def test_format_status_response_pending(self):
        """Test status response for pending execution."""
        result = format_status_response(
            team_id="test-team-123",
            topic="Climate Change",
            created_at="2025-10-16T10:00:00Z",
            status="pending"
        )
        
        # Validate JSON-LD structure
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "ResearchReport"
        assert result["identifier"] == "test-team-123"
        assert result["name"] == "Climate Change"
        assert result["dateCreated"] == "2025-10-16T10:00:00Z"
        assert result["status"] == "pending"
        
        # Should not have optional fields for pending status
        assert "numberOfEntities" not in result
        assert "duration" not in result
    
    def test_format_status_response_running(self):
        """Test status response for running execution."""
        result = format_status_response(
            team_id="test-team-456",
            topic="AI Ethics",
            created_at="2025-10-16T10:00:00Z",
            status="running",
            modified_at="2025-10-16T10:02:00Z"
        )
        
        assert result["status"] == "running"
        assert result["dateModified"] == "2025-10-16T10:02:00Z"
        assert "numberOfEntities" not in result
        assert "duration" not in result
    
    def test_format_status_response_completed(self):
        """Test status response for completed execution."""
        result = format_status_response(
            team_id="test-team-789",
            topic="Renewable Energy",
            created_at="2025-10-16T10:00:00Z",
            status="completed",
            modified_at="2025-10-16T10:05:00Z",
            entity_count=15,
            duration_seconds=323.5
        )
        
        assert result["status"] == "completed"
        assert result["dateModified"] == "2025-10-16T10:05:00Z"
        assert result["numberOfEntities"] == 15
        assert result["duration"] == "PT5M23S"
    
    def test_format_status_response_failed(self):
        """Test status response for failed execution."""
        result = format_status_response(
            team_id="test-team-999",
            topic="Failed Topic",
            created_at="2025-10-16T10:00:00Z",
            status="failed",
            modified_at="2025-10-16T10:01:00Z"
        )
        
        assert result["status"] == "failed"
        assert result["dateModified"] == "2025-10-16T10:01:00Z"
        assert "numberOfEntities" not in result
        assert "duration" not in result
    
    def test_format_status_response_entity_count_only_for_completed(self):
        """Test that entity count is only included for completed status."""
        # Entity count provided but status is not completed
        result = format_status_response(
            team_id="test-team-111",
            topic="Test Topic",
            created_at="2025-10-16T10:00:00Z",
            status="running",
            entity_count=10
        )
        
        # Should not include entity count for non-completed status
        assert "numberOfEntities" not in result
    
    def test_format_status_response_duration_only_for_completed(self):
        """Test that duration is only included for completed status."""
        # Duration provided but status is not completed
        result = format_status_response(
            team_id="test-team-222",
            topic="Test Topic",
            created_at="2025-10-16T10:00:00Z",
            status="pending",
            duration_seconds=100.0
        )
        
        # Should not include duration for non-completed status
        assert "duration" not in result
    
    def test_format_status_response_required_fields(self):
        """Test that all required JSON-LD fields are present."""
        result = format_status_response(
            team_id="test-team-333",
            topic="Test Topic",
            created_at="2025-10-16T10:00:00Z",
            status="pending"
        )
        
        required_fields = ["@context", "@type", "identifier", "name", "dateCreated", "status"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


class TestFormatListResponse:
    """Tests for format_list_response function."""
    
    def test_format_list_response_empty(self):
        """Test list response with empty team list."""
        result = format_list_response(teams=[])
        
        # Validate JSON-LD structure
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "ItemList"
        assert result["numberOfItems"] == 0
        assert result["itemListElement"] == []
    
    def test_format_list_response_single_team(self):
        """Test list response with single team."""
        teams = [
            {
                "team_id": "test-team-123",
                "topic": "Climate Change",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            }
        ]
        
        result = format_list_response(teams)
        
        assert result["numberOfItems"] == 1
        assert len(result["itemListElement"]) == 1
        
        # Validate first item
        item = result["itemListElement"][0]
        assert item["@type"] == "ListItem"
        assert item["position"] == 1
        assert item["item"]["@type"] == "ResearchReport"
        assert item["item"]["identifier"] == "test-team-123"
        assert item["item"]["name"] == "Climate Change"
        assert item["item"]["status"] == "completed"
    
    def test_format_list_response_multiple_teams(self):
        """Test list response with multiple teams."""
        teams = [
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
            },
            {
                "team_id": "team-3",
                "topic": "Renewable Energy",
                "status": "pending",
                "created_at": "2025-10-16T12:00:00Z"
            }
        ]
        
        result = format_list_response(teams)
        
        assert result["numberOfItems"] == 3
        assert len(result["itemListElement"]) == 3
        
        # Validate positions are sequential
        for i, item in enumerate(result["itemListElement"], start=1):
            assert item["position"] == i
            assert item["@type"] == "ListItem"
    
    def test_format_list_response_with_modified_at(self):
        """Test list response includes dateModified when present."""
        teams = [
            {
                "team_id": "team-1",
                "topic": "Test Topic",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z",
                "updated_at": "2025-10-16T10:05:00Z"
            }
        ]
        
        result = format_list_response(teams)
        
        item = result["itemListElement"][0]["item"]
        assert item["dateModified"] == "2025-10-16T10:05:00Z"
    
    def test_format_list_response_with_entity_count(self):
        """Test list response includes entity count for completed teams."""
        teams = [
            {
                "team_id": "team-1",
                "topic": "Test Topic",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z",
                "sachstand": {
                    "@type": "ResearchReport",
                    "hasPart": [
                        {"@type": "Person", "name": "John Doe"},
                        {"@type": "Organization", "name": "Test Org"},
                        {"@type": "Event", "name": "Test Event"}
                    ]
                }
            }
        ]
        
        result = format_list_response(teams)
        
        item = result["itemListElement"][0]["item"]
        assert item["numberOfEntities"] == 3
    
    def test_format_list_response_no_entity_count_for_non_completed(self):
        """Test list response does not include entity count for non-completed teams."""
        teams = [
            {
                "team_id": "team-1",
                "topic": "Test Topic",
                "status": "running",
                "created_at": "2025-10-16T10:00:00Z",
                "sachstand": {
                    "hasPart": [{"@type": "Person"}]
                }
            }
        ]
        
        result = format_list_response(teams)
        
        item = result["itemListElement"][0]["item"]
        assert "numberOfEntities" not in item
    
    def test_format_list_response_with_custom_total_count(self):
        """Test list response with custom total count (for pagination)."""
        teams = [
            {
                "team_id": "team-1",
                "topic": "Test Topic",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            }
        ]
        
        result = format_list_response(teams, total_count=100)
        
        # Total count should be custom value, not len(teams)
        assert result["numberOfItems"] == 100
        assert len(result["itemListElement"]) == 1
    
    def test_format_list_response_handles_id_field(self):
        """Test list response handles 'id' field as fallback for 'team_id'."""
        teams = [
            {
                "id": "team-123",  # Using 'id' instead of 'team_id'
                "topic": "Test Topic",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            }
        ]
        
        result = format_list_response(teams)
        
        item = result["itemListElement"][0]["item"]
        assert item["identifier"] == "team-123"
    
    def test_format_list_response_required_fields(self):
        """Test that all required JSON-LD fields are present."""
        teams = [
            {
                "team_id": "team-1",
                "topic": "Test Topic",
                "status": "completed",
                "created_at": "2025-10-16T10:00:00Z"
            }
        ]
        
        result = format_list_response(teams)
        
        # Check top-level required fields
        required_fields = ["@context", "@type", "numberOfItems", "itemListElement"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check item required fields
        item = result["itemListElement"][0]
        assert item["@type"] == "ListItem"
        assert "position" in item
        assert "item" in item
        
        # Check nested item required fields
        nested_item = item["item"]
        required_item_fields = ["@type", "identifier", "name", "dateCreated", "status"]
        for field in required_item_fields:
            assert field in nested_item, f"Missing required item field: {field}"


class TestFormatResultsResponse:
    """Tests for format_results_response function."""
    
    def test_format_results_response_passthrough(self):
        """Test that results response passes through sachstand as-is."""
        sachstand = {
            "@context": "https://schema.org",
            "@type": "ResearchReport",
            "name": "Sachstand: Climate Change",
            "dateCreated": "2025-10-16T10:05:00Z",
            "hasPart": [
                {
                    "@type": "Person",
                    "name": "John Doe",
                    "description": "Climate scientist"
                }
            ]
        }
        
        result = format_results_response(sachstand)
        
        # Should return exact same object
        assert result == sachstand
        assert result["@type"] == "ResearchReport"
        assert result["name"] == "Sachstand: Climate Change"
        assert len(result["hasPart"]) == 1
    
    def test_format_results_response_with_multiple_entities(self):
        """Test results response with multiple entities."""
        sachstand = {
            "@context": "https://schema.org",
            "@type": "ResearchReport",
            "name": "Sachstand: AI Ethics",
            "hasPart": [
                {"@type": "Person", "name": "Person 1"},
                {"@type": "Organization", "name": "Org 1"},
                {"@type": "Event", "name": "Event 1"}
            ]
        }
        
        result = format_results_response(sachstand)
        
        assert result == sachstand
        assert len(result["hasPart"]) == 3
    
    def test_format_results_response_empty_entities(self):
        """Test results response with no entities."""
        sachstand = {
            "@context": "https://schema.org",
            "@type": "ResearchReport",
            "name": "Sachstand: Empty",
            "hasPart": []
        }
        
        result = format_results_response(sachstand)
        
        assert result == sachstand
        assert result["hasPart"] == []


class TestFormatErrorResponse:
    """Tests for format_error_response function."""
    
    def test_format_error_response_basic(self):
        """Test basic error response formatting."""
        result = format_error_response(
            code="EXECUTION_NOT_FOUND",
            message="Execution with ID xyz not found"
        )
        
        # Validate JSON-LD structure
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "ErrorResponse"
        
        # Validate error structure
        assert result["error"]["code"] == "EXECUTION_NOT_FOUND"
        assert result["error"]["message"] == "Execution with ID xyz not found"
        assert "timestamp" in result["error"]
        
        # Validate timestamp is ISO 8601 format
        timestamp = result["error"]["timestamp"]
        # Should be parseable as ISO 8601
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_format_error_response_with_custom_timestamp(self):
        """Test error response with custom timestamp."""
        custom_timestamp = "2025-10-16T10:00:00Z"
        
        result = format_error_response(
            code="BACKEND_UNAVAILABLE",
            message="FastAPI backend is not responding",
            timestamp=custom_timestamp
        )
        
        assert result["error"]["timestamp"] == custom_timestamp
    
    def test_format_error_response_different_error_codes(self):
        """Test error response with different error codes."""
        error_codes = [
            "EXECUTION_NOT_FOUND",
            "EXECUTION_NOT_COMPLETED",
            "BACKEND_UNAVAILABLE",
            "INVALID_PARAMETER",
            "TIMEOUT_ERROR"
        ]
        
        for code in error_codes:
            result = format_error_response(
                code=code,
                message=f"Test error for {code}"
            )
            
            assert result["error"]["code"] == code
            assert code in result["error"]["message"]
    
    def test_format_error_response_required_fields(self):
        """Test that all required JSON-LD fields are present."""
        result = format_error_response(
            code="TEST_ERROR",
            message="Test error message"
        )
        
        # Check top-level required fields
        required_fields = ["@context", "@type", "error"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check error required fields
        required_error_fields = ["code", "message", "timestamp"]
        for field in required_error_fields:
            assert field in result["error"], f"Missing required error field: {field}"


class TestFormatISO8601Duration:
    """Tests for _format_iso8601_duration helper function."""
    
    def test_format_duration_seconds_only(self):
        """Test duration formatting with seconds only."""
        assert _format_iso8601_duration(30) == "PT30S"
        assert _format_iso8601_duration(45.7) == "PT45S"
    
    def test_format_duration_minutes_and_seconds(self):
        """Test duration formatting with minutes and seconds."""
        assert _format_iso8601_duration(90) == "PT1M30S"
        assert _format_iso8601_duration(323) == "PT5M23S"
        assert _format_iso8601_duration(125.8) == "PT2M5S"
    
    def test_format_duration_hours_minutes_seconds(self):
        """Test duration formatting with hours, minutes, and seconds."""
        assert _format_iso8601_duration(3661) == "PT1H1M1S"
        assert _format_iso8601_duration(3600) == "PT1H"
        assert _format_iso8601_duration(3723) == "PT1H2M3S"
        assert _format_iso8601_duration(7384) == "PT2H3M4S"
    
    def test_format_duration_zero_seconds(self):
        """Test duration formatting with zero seconds."""
        assert _format_iso8601_duration(0) == "PT0S"
    
    def test_format_duration_exact_minutes(self):
        """Test duration formatting with exact minutes (no seconds)."""
        assert _format_iso8601_duration(60) == "PT1M"
        assert _format_iso8601_duration(300) == "PT5M"
        assert _format_iso8601_duration(600) == "PT10M"
    
    def test_format_duration_exact_hours(self):
        """Test duration formatting with exact hours (no minutes or seconds)."""
        assert _format_iso8601_duration(3600) == "PT1H"
        assert _format_iso8601_duration(7200) == "PT2H"
        assert _format_iso8601_duration(10800) == "PT3H"
    
    def test_format_duration_hours_and_seconds(self):
        """Test duration formatting with hours and seconds (no minutes)."""
        assert _format_iso8601_duration(3605) == "PT1H5S"
        assert _format_iso8601_duration(7215) == "PT2H15S"
    
    def test_format_duration_large_values(self):
        """Test duration formatting with large values."""
        # 24 hours
        assert _format_iso8601_duration(86400) == "PT24H"
        # 25 hours, 30 minutes, 45 seconds
        assert _format_iso8601_duration(91845) == "PT25H30M45S"
