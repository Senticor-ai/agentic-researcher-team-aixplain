#!/usr/bin/env python3
"""
Demo script to test logging implementation.

This script demonstrates the logging functionality without requiring
a running FastAPI backend or MCP client.
"""

import logging
import sys
from datetime import datetime, timezone

# Setup logging to stderr (same as main.py)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


def test_custom_exceptions():
    """Test custom exception classes and their JSON-LD formatting."""
    from errors import (
        MCPError,
        ExecutionNotFoundError,
        ExecutionNotCompletedError,
        BackendUnavailableError
    )
    
    logger.info("Testing custom exception classes...")
    
    # Test ExecutionNotFoundError
    e1 = ExecutionNotFoundError("test-execution-123")
    logger.debug(f"Created ExecutionNotFoundError: {e1.code}")
    json_ld = e1.to_json_ld()
    logger.debug(f"JSON-LD format: {json_ld}")
    
    # Test ExecutionNotCompletedError
    e2 = ExecutionNotCompletedError("test-execution-456", "running")
    logger.debug(f"Created ExecutionNotCompletedError: {e2.code}")
    
    # Test BackendUnavailableError
    e3 = BackendUnavailableError("http://localhost:8000", "Connection refused")
    logger.debug(f"Created BackendUnavailableError: {e3.code}")
    
    logger.info("✓ Custom exception tests passed")


def test_formatters():
    """Test response formatters with logging."""
    from formatters import (
        format_spawn_response,
        format_status_response,
        format_list_response,
        format_error_response
    )
    
    logger.info("Testing response formatters...")
    
    # Test spawn response
    spawn_resp = format_spawn_response(
        team_id="abc-123",
        topic="Test Topic",
        created_at=datetime.now(timezone.utc).isoformat(),
        status="pending"
    )
    logger.debug(f"Spawn response type: {spawn_resp.get('@type')}")
    
    # Test status response
    status_resp = format_status_response(
        team_id="abc-123",
        topic="Test Topic",
        created_at=datetime.now(timezone.utc).isoformat(),
        status="completed",
        entity_count=15,
        duration_seconds=123.45
    )
    logger.debug(f"Status response has {status_resp.get('numberOfEntities')} entities")
    
    # Test list response
    teams = [
        {
            "team_id": "team-1",
            "topic": "Topic 1",
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "team_id": "team-2",
            "topic": "Topic 2",
            "status": "running",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    list_resp = format_list_response(teams)
    logger.debug(f"List response has {list_resp.get('numberOfItems')} items")
    
    # Test error response
    error_resp = format_error_response("TEST_ERROR", "This is a test error")
    logger.debug(f"Error response code: {error_resp['error']['code']}")
    
    logger.info("✓ Formatter tests passed")


def test_logging_levels():
    """Test different logging levels."""
    logger.info("Testing different logging levels...")
    
    logger.debug("This is a DEBUG message - detailed diagnostic info")
    logger.info("This is an INFO message - general informational message")
    logger.warning("This is a WARNING message - something unexpected happened")
    logger.error("This is an ERROR message - a serious problem occurred")
    
    # Test error with stack trace
    try:
        raise ValueError("Test exception for logging")
    except ValueError as e:
        logger.error(f"Caught exception: {e}", exc_info=True)
    
    logger.info("✓ Logging level tests passed")


def main():
    """Run all logging tests."""
    logger.info("=" * 60)
    logger.info("MCP Server Logging Implementation Demo")
    logger.info("=" * 60)
    
    try:
        test_custom_exceptions()
        print()  # Blank line for readability
        
        test_formatters()
        print()
        
        test_logging_levels()
        print()
        
        logger.info("=" * 60)
        logger.info("All tests completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
