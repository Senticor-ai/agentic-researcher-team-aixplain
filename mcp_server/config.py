"""Configuration module for the MCP server.

This module handles loading and validating configuration from
environment variables.
"""

import logging
import os
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class Config(BaseModel):
    """Configuration for the LibreChat MCP server.
    
    All configuration values can be set via environment variables.
    The MCP server is completely stateless - all state is managed by the FastAPI backend.
    """
    
    # FastAPI Backend Configuration (Required)
    fastapi_base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for the FastAPI backend"
    )
    
    # HTTP Client Configuration
    http_timeout: float = Field(
        default=30.0,
        description="HTTP request timeout in seconds"
    )
    
    # MCP Server Configuration
    server_name: str = Field(
        default="librechat-osint-mcp",
        description="MCP server name"
    )
    
    server_version: str = Field(
        default="0.1.0",
        description="MCP server version"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper
    
    @field_validator("fastapi_base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL."""
        if not v:
            raise ValueError("fastapi_base_url is required")
        # Remove trailing slash for consistency
        return v.rstrip("/")
    
    @field_validator("http_timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("http_timeout must be positive")
        return v
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Environment variables:
        - FASTAPI_BASE_URL: Base URL for the FastAPI backend (required)
        - HTTP_TIMEOUT: HTTP request timeout in seconds (default: 30.0)
        - MCP_SERVER_NAME: MCP server name (default: librechat-osint-mcp)
        - MCP_SERVER_VERSION: MCP server version (default: 0.1.0)
        - LOG_LEVEL: Logging level (default: INFO)
        
        Returns:
            Config instance with values from environment
        """
        # Note: Logger may not be configured yet when this is called
        # Actual logging happens in main.py after setup_logging()
        config = cls(
            fastapi_base_url=os.getenv("FASTAPI_BASE_URL", "http://localhost:8000"),
            http_timeout=float(os.getenv("HTTP_TIMEOUT", "30.0")),
            server_name=os.getenv("MCP_SERVER_NAME", "librechat-osint-mcp"),
            server_version=os.getenv("MCP_SERVER_VERSION", "0.1.0"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        return config
