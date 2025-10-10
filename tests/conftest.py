"""
Pytest configuration and fixtures
"""
import os
import sys
from unittest.mock import Mock, MagicMock

# Set dummy API key before any imports
os.environ["AIXPLAIN_API_KEY"] = "test-api-key-for-testing"

# Mock the aixplain module to avoid API key validation during tests
mock_aixplain = MagicMock()
mock_agent_factory = MagicMock()
mock_agent = MagicMock()
mock_agent.id = "test-agent-id"
mock_agent.run.return_value = {"data": "test response", "status": "completed"}
mock_agent_factory.create.return_value = mock_agent
mock_agent_factory.get.return_value = mock_agent
mock_aixplain.factories.AgentFactory = mock_agent_factory
mock_aixplain.enums.Function = MagicMock()

sys.modules['aixplain'] = mock_aixplain
sys.modules['aixplain.factories'] = mock_aixplain.factories
sys.modules['aixplain.enums'] = mock_aixplain.enums
