"""
Register Validation Tools with aixplain SDK

This module registers the schema.org validator and URL verifier tools
with the aixplain SDK so they can be used by agents.
"""
import logging
from typing import Optional, Tuple
from aixplain.factories import ToolFactory
from api.schema_org_validator_tool import validate_schema_org
from api.url_verifier_tool import verify_urls

logger = logging.getLogger(__name__)


class ValidationToolRegistry:
    """
    Registry for validation tools
    """
    
    # Tool IDs (will be set after registration)
    SCHEMA_VALIDATOR_TOOL_ID: Optional[str] = None
    URL_VERIFIER_TOOL_ID: Optional[str] = None
    
    @classmethod
    def register_schema_validator(cls) -> str:
        """
        Register schema.org validator tool with aixplain
        
        Returns:
            Tool ID string
        """
        try:
            logger.info("Registering schema.org validator tool...")
            
            tool = ToolFactory.create(
                name="Schema.org Validator",
                description=(
                    "Validates entities against schema.org specifications. "
                    "Checks for valid @context, @type, and properties. "
                    "Returns validation results with issues and suggested corrections."
                ),
                function=validate_schema_org,
                parameters={
                    "entity": {
                        "type": "object",
                        "description": "Entity object to validate against schema.org specifications",
                        "required": True
                    }
                }
            )
            
            cls.SCHEMA_VALIDATOR_TOOL_ID = tool.id
            logger.info(f"Schema.org validator tool registered with ID: {tool.id}")
            
            return tool.id
            
        except Exception as e:
            logger.error(f"Failed to register schema.org validator tool: {e}")
            raise
    
    @classmethod
    def register_url_verifier(cls) -> str:
        """
        Register URL verifier tool with aixplain
        
        Returns:
            Tool ID string
        """
        try:
            logger.info("Registering URL verifier tool...")
            
            tool = ToolFactory.create(
                name="URL Verifier",
                description=(
                    "Verifies URLs are valid and accessible. "
                    "Checks URL format and performs HTTP HEAD requests to verify accessibility. "
                    "Returns verification results with status codes and issues."
                ),
                function=verify_urls,
                parameters={
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to verify for validity and accessibility",
                        "required": True
                    }
                }
            )
            
            cls.URL_VERIFIER_TOOL_ID = tool.id
            logger.info(f"URL verifier tool registered with ID: {tool.id}")
            
            return tool.id
            
        except Exception as e:
            logger.error(f"Failed to register URL verifier tool: {e}")
            raise
    
    @classmethod
    def register_all_tools(cls) -> Tuple[str, str]:
        """
        Register all validation tools with aixplain
        
        Returns:
            Tuple of (schema_validator_tool_id, url_verifier_tool_id)
        """
        schema_validator_id = cls.register_schema_validator()
        url_verifier_id = cls.register_url_verifier()
        
        logger.info("All validation tools registered successfully")
        
        return schema_validator_id, url_verifier_id
    
    @classmethod
    def get_tool_ids(cls) -> Tuple[Optional[str], Optional[str]]:
        """
        Get registered tool IDs
        
        Returns:
            Tuple of (schema_validator_tool_id, url_verifier_tool_id)
        """
        return cls.SCHEMA_VALIDATOR_TOOL_ID, cls.URL_VERIFIER_TOOL_ID


# Convenience function for easy import
def register_validation_tools() -> Tuple[str, str]:
    """
    Register validation tools and return their IDs
    
    Returns:
        Tuple of (schema_validator_tool_id, url_verifier_tool_id)
    """
    return ValidationToolRegistry.register_all_tools()
