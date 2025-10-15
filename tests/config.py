"""
Test configuration module

Centralizes test configuration including API URLs from environment variables.
Reads from .env file - no hardcoded defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API Configuration - read from .env (API_PORT, API_HOST)
API_PORT = os.getenv("API_PORT")
API_HOST = os.getenv("API_HOST", "localhost")  # localhost is reasonable default

if not API_PORT:
    raise ValueError(
        "API_PORT not found in .env file. "
        "Please set API_PORT in your .env file (e.g., API_PORT=8080)"
    )

API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
API_V1_BASE = f"{API_BASE_URL}/api/v1"

# Test timeouts - can be overridden with TEST_* prefix
DEFAULT_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "120"))  # seconds
SLOW_TEST_TIMEOUT = int(os.getenv("TEST_SLOW_TIMEOUT", "300"))  # seconds
POLL_INTERVAL = int(os.getenv("TEST_POLL_INTERVAL", "5"))  # seconds

# Test configuration
MAX_RETRIES = int(os.getenv("TEST_MAX_RETRIES", "3"))
