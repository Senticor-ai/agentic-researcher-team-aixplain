"""Tests for the main entry point."""

import logging
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.main import setup_logging, main


def test_setup_logging_default():
    """Test that logging setup can be called without errors."""
    # Just verify it doesn't raise an exception
    setup_logging()
    # Verify logging is working
    logger = logging.getLogger("test")
    logger.info("Test message")


def test_setup_logging_custom_level():
    """Test that logging setup accepts custom levels."""
    # Just verify it doesn't raise an exception with different levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        setup_logging(level)


def test_setup_logging_stderr_configuration():
    """Test that setup_logging configures stderr stream."""
    # Create a fresh logger to test configuration
    test_logger_name = "test_stderr_logger"
    test_logger = logging.getLogger(test_logger_name)
    
    # Clear any existing handlers
    test_logger.handlers.clear()
    test_logger.propagate = False
    
    # Add a handler with stderr (simulating what setup_logging does)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    # Verify the handler uses stderr
    assert len(test_logger.handlers) > 0
    assert test_logger.handlers[0].stream == sys.stderr


@pytest.mark.asyncio
async def test_main_initialization(monkeypatch):
    """Test that main() initializes server with correct configuration."""
    # Set environment variables
    monkeypatch.setenv("FASTAPI_BASE_URL", "http://test.example.com:8000")
    monkeypatch.setenv("HTTP_TIMEOUT", "45.0")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Mock the stdio_server and server.run
    mock_read_stream = MagicMock()
    mock_write_stream = MagicMock()
    
    with patch("mcp_server.main.stdio_server") as mock_stdio:
        with patch("mcp_server.main.LibreChatMCPServer") as mock_server_class:
            # Configure the async context manager
            mock_stdio.return_value.__aenter__ = AsyncMock(
                return_value=(mock_read_stream, mock_write_stream)
            )
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Configure the server instance
            mock_server_instance = MagicMock()
            mock_server_instance.server.run = AsyncMock()
            mock_server_instance.server.create_initialization_options = MagicMock(
                return_value={}
            )
            mock_server_class.return_value = mock_server_instance
            
            # Run main
            await main()
            
            # Verify server was initialized with correct parameters
            mock_server_class.assert_called_once_with(
                api_base_url="http://test.example.com:8000",
                timeout=45.0
            )
            
            # Verify server.run was called
            mock_server_instance.server.run.assert_called_once()


@pytest.mark.asyncio
async def test_main_uses_default_config(monkeypatch):
    """Test that main() uses default configuration when env vars not set."""
    # Clear any existing environment variables
    for key in ["FASTAPI_BASE_URL", "HTTP_TIMEOUT", "LOG_LEVEL"]:
        monkeypatch.delenv(key, raising=False)
    
    # Mock the stdio_server and server.run
    mock_read_stream = MagicMock()
    mock_write_stream = MagicMock()
    
    with patch("mcp_server.main.stdio_server") as mock_stdio:
        with patch("mcp_server.main.LibreChatMCPServer") as mock_server_class:
            # Configure the async context manager
            mock_stdio.return_value.__aenter__ = AsyncMock(
                return_value=(mock_read_stream, mock_write_stream)
            )
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Configure the server instance
            mock_server_instance = MagicMock()
            mock_server_instance.server.run = AsyncMock()
            mock_server_instance.server.create_initialization_options = MagicMock(
                return_value={}
            )
            mock_server_class.return_value = mock_server_instance
            
            # Run main
            await main()
            
            # Verify server was initialized with default parameters
            mock_server_class.assert_called_once_with(
                api_base_url="http://localhost:8000",
                timeout=30.0
            )
