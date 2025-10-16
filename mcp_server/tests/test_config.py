"""Tests for the configuration module."""

import os
import pytest
from pydantic import ValidationError

from mcp_server.config import Config


def test_config_defaults():
    """Test that Config has sensible defaults."""
    config = Config()
    
    assert config.fastapi_base_url == "http://localhost:8000"
    assert config.http_timeout == 30.0
    assert config.server_name == "librechat-osint-mcp"
    assert config.server_version == "0.1.0"
    assert config.log_level == "INFO"


def test_config_from_env(monkeypatch):
    """Test loading configuration from environment variables."""
    # Set environment variables
    monkeypatch.setenv("FASTAPI_BASE_URL", "http://example.com:9000")
    monkeypatch.setenv("HTTP_TIMEOUT", "60.0")
    monkeypatch.setenv("MCP_SERVER_NAME", "test-server")
    monkeypatch.setenv("MCP_SERVER_VERSION", "1.0.0")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    config = Config.from_env()
    
    assert config.fastapi_base_url == "http://example.com:9000"
    assert config.http_timeout == 60.0
    assert config.server_name == "test-server"
    assert config.server_version == "1.0.0"
    assert config.log_level == "DEBUG"


def test_config_base_url_normalization():
    """Test that base URL trailing slashes are removed."""
    config = Config(fastapi_base_url="http://localhost:8000/")
    assert config.fastapi_base_url == "http://localhost:8000"
    
    config = Config(fastapi_base_url="http://localhost:8000///")
    assert config.fastapi_base_url == "http://localhost:8000"


def test_config_invalid_log_level():
    """Test that invalid log levels are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Config(log_level="INVALID")
    
    assert "log_level must be one of" in str(exc_info.value)


def test_config_invalid_timeout():
    """Test that invalid timeouts are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Config(http_timeout=0)
    
    assert "http_timeout must be positive" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        Config(http_timeout=-5.0)
    
    assert "http_timeout must be positive" in str(exc_info.value)


def test_config_empty_base_url():
    """Test that empty base URL is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Config(fastapi_base_url="")
    
    assert "fastapi_base_url is required" in str(exc_info.value)


def test_config_log_level_case_insensitive():
    """Test that log level validation is case-insensitive."""
    config = Config(log_level="debug")
    assert config.log_level == "DEBUG"
    
    config = Config(log_level="Info")
    assert config.log_level == "INFO"
    
    config = Config(log_level="WARNING")
    assert config.log_level == "WARNING"
