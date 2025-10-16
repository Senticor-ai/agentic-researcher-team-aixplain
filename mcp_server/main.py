"""Main entry point for the LibreChat MCP server.

This module initializes and runs the MCP server with configuration
loaded from environment variables.

The server uses stdio transport to communicate with LibreChat via the MCP protocol.
"""

import asyncio
import logging
import sys

from mcp.server.stdio import stdio_server

from .config import Config
from .server import LibreChatMCPServer


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the MCP server.
    
    Logs are written to stderr to avoid interfering with stdio transport.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr  # Use stderr to avoid interfering with stdio transport
    )


async def main() -> None:
    """Initialize and run the MCP server.
    
    This function:
    1. Loads configuration from environment variables
    2. Sets up logging
    3. Initializes the stateless MCP server
    4. Runs the server using stdio transport
    """
    # Load configuration from environment variables
    config = Config.from_env()
    
    # Setup logging (writes to stderr)
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {config.server_name} v{config.server_version}")
    logger.info(f"FastAPI Backend: {config.fastapi_base_url}")
    logger.info(f"HTTP Timeout: {config.http_timeout}s")
    logger.info(f"Log Level: {config.log_level}")
    
    # Initialize the stateless MCP server
    mcp_server = LibreChatMCPServer(
        api_base_url=config.fastapi_base_url,
        timeout=config.http_timeout
    )
    
    logger.info("MCP server initialized successfully")
    logger.info("Starting stdio transport...")
    
    # Run the server using stdio transport
    # This will handle communication with LibreChat via stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            mcp_server.server.create_initialization_options()
        )


def run() -> None:
    """Entry point for the MCP server.
    
    This function is called when the package is executed as a module
    or via the console script defined in pyproject.toml.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        logger = logging.getLogger(__name__)
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()
