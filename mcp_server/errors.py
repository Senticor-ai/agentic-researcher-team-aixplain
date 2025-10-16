"""Custom exception classes for MCP server error handling."""

from datetime import datetime, timezone
from typing import Any, Dict


class MCPError(Exception):
    """Base exception class for MCP server errors."""
    
    def __init__(self, code: str, message: str):
        """
        Initialize MCP error.
        
        Args:
            code: Error code identifier
            message: Human-readable error message
        """
        self.code = code
        self.message = message
        super().__init__(message)
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Convert error to JSON-LD format.
        
        Returns:
            JSON-LD formatted error response
        """
        return {
            "@context": "https://schema.org",
            "@type": "ErrorResponse",
            "error": {
                "code": self.code,
                "message": self.message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


class ExecutionNotFoundError(MCPError):
    """Exception raised when an execution ID is not found."""
    
    def __init__(self, execution_id: str):
        """
        Initialize execution not found error.
        
        Args:
            execution_id: The execution ID that was not found
        """
        super().__init__(
            code="EXECUTION_NOT_FOUND",
            message=f"Execution with ID '{execution_id}' not found"
        )
        self.execution_id = execution_id


class ExecutionNotCompletedError(MCPError):
    """Exception raised when attempting to retrieve results for an incomplete execution."""
    
    def __init__(self, execution_id: str, current_status: str):
        """
        Initialize execution not completed error.
        
        Args:
            execution_id: The execution ID
            current_status: Current status of the execution
        """
        super().__init__(
            code="EXECUTION_NOT_COMPLETED",
            message=f"Execution '{execution_id}' is not completed. Current status: {current_status}"
        )
        self.execution_id = execution_id
        self.current_status = current_status


class BackendUnavailableError(MCPError):
    """Exception raised when the FastAPI backend is unavailable."""
    
    def __init__(self, base_url: str, details: str = None):
        """
        Initialize backend unavailable error.
        
        Args:
            base_url: The FastAPI backend base URL
            details: Optional additional details about the error
        """
        message = f"FastAPI backend at '{base_url}' is unavailable"
        if details:
            message += f": {details}"
        
        super().__init__(
            code="BACKEND_UNAVAILABLE",
            message=message
        )
        self.base_url = base_url
        self.details = details
