"""
Central configuration for Honeycomb OSINT Agent Team System
"""
import os
from typing import Dict


class Config:
    """Central configuration for models, tools, and system settings"""
    
    # Model Configuration
    # Each agent is explicitly configured with a specific model
    # All agents use GPT-4o for best quality and compatibility with aixplain TeamAgent
    
    # Available Models
    GPT_4O = "6646261c6eb563165658bbb1"  # GPT-4o - Best quality, proven to work
    
    # Agent-Specific Model Configuration
    SEARCH_AGENT_MODEL = GPT_4O  # Search Agent: entity extraction, needs strong reasoning
    WIKIPEDIA_AGENT_MODEL = GPT_4O  # Wikipedia Agent: entity matching and linking
    TEAM_AGENT_MODEL = GPT_4O  # Team micro agents: Mentalist, Inspector, Orchestrator, Response Generator
    
    # Legacy support for existing code
    DEFAULT_MODEL = "gpt4o"
    MODELS: Dict[str, str] = {
        "gpt4o": GPT_4O,
    }
    
    # Tool IDs from aixplain marketplace
    TOOL_IDS: Dict[str, str] = {
        "tavily_search": "6736411cf127849667606689",  # Tavily Search API
        "wikipedia": "6633fd59821ee31dd914e232",      # Wikipedia
        "google_search": "65c51c556eb563350f6e1bb1",   # Google Search (Scale SERP)
    }
    
    # Agent Instructions Directory
    INSTRUCTIONS_DIR = "api/instructions"
    
    # Database Configuration
    DB_PATH = os.getenv("DB_PATH", "./data/teams.db")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ]
    
    @classmethod
    def get_model_id(cls, model: str = None) -> str:
        """
        Get model ID with fallback to default
        
        Args:
            model: Model name ("production" or "testing"), None uses default
            
        Returns:
            Model ID string
        """
        if model is None:
            model = cls.DEFAULT_MODEL
        return cls.MODELS.get(model, cls.MODELS[cls.DEFAULT_MODEL])
    
    @classmethod
    def get_tool_id(cls, tool_name: str) -> str:
        """
        Get tool ID by name
        
        Args:
            tool_name: Name of the tool (e.g., "tavily_search", "wikipedia")
            
        Returns:
            Tool ID string
            
        Raises:
            KeyError: If tool name not found
        """
        return cls.TOOL_IDS[tool_name]
