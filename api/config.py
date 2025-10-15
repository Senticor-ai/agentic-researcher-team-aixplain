"""
Central configuration for Honeycomb OSINT Agent Team System
"""
import os
from typing import Dict


class Config:
    """Central configuration for models, tools, and system settings"""
    
    # Model Configuration
    # Each agent is explicitly configured with a specific model
    # All agents use Llama 3.3 70B Versatile (Groq) for best quality and compatibility with aixplain TeamAgent
    
    # Available Models
    LLAMA_3_3_70B_VERSATILE = "677c16166eb563bb611623c1"  # Llama 3.3 70B Versatile (Groq) - Current model
    GPT_4O = "6646261c6eb563165658bbb1"  # GPT-4o
    QWEN3_235B = "6810d040a289e15e3e5dd141"  # Qwen3 235B
    GEMINI_2_FLASH_EXP = "6759db476eb56303857a07c1"  # Gemini 2.0 Flash (Exp)
    GPT_OSS_120B = "6895f768d50c89537c1cf24e"  # GPT OSS 120b - Open source model
    GPT_5_MINI = "6895d6d1d50c89537c1cf237"  # GPT-5 Mini - Latest model
    
    # Agent-Specific Model Configuration
    SEARCH_AGENT_MODEL = LLAMA_3_3_70B_VERSATILE  # Search Agent: entity extraction, needs strong reasoning
    WIKIPEDIA_AGENT_MODEL = LLAMA_3_3_70B_VERSATILE  # Wikipedia Agent: entity matching and linking
    TEAM_AGENT_MODEL = LLAMA_3_3_70B_VERSATILE  # Team micro agents: Mentalist, Inspector, Orchestrator, Response Generator
    
    # Legacy support for existing code
    DEFAULT_MODEL = "llama33_70b"
    MODELS: Dict[str, str] = {
        "llama33_70b": LLAMA_3_3_70B_VERSATILE,
        "gpt4o": GPT_4O,
        "qwen3235b": QWEN3_235B,
        "gemini2flash": GEMINI_2_FLASH_EXP,
        "gptoss120b": GPT_OSS_120B,
        "gpt5mini": GPT_5_MINI,
    }
    
    # Model ID to display name mapping
    MODEL_NAMES: Dict[str, str] = {
        LLAMA_3_3_70B_VERSATILE: "Llama 3.3 70B Versatile (Groq)",
        GPT_4O: "GPT-4o",
        QWEN3_235B: "Qwen3 235B",
        GEMINI_2_FLASH_EXP: "Gemini 2.0 Flash (Exp)",
        GPT_OSS_120B: "GPT OSS 120b",
        GPT_5_MINI: "GPT-5 Mini",
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
    
    @classmethod
    def get_model_name(cls, model_id: str = None) -> str:
        """
        Get human-readable model name from model ID
        
        Args:
            model_id: Model ID, defaults to TEAM_AGENT_MODEL if None
            
        Returns:
            Human-readable model name
        """
        if model_id is None:
            model_id = cls.TEAM_AGENT_MODEL
        return cls.MODEL_NAMES.get(model_id, f"Unknown Model ({model_id})")
