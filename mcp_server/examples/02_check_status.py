#!/usr/bin/env python3
"""Example script to check execution status.

This script demonstrates how to check the status of a running
or completed agent team execution.

Usage:
    python examples/02_check_status.py <team_id>
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import mcp_server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.fastapi_client import FastAPIClient


async def main():
    """Check the status of an agent team execution."""
    # Check if team_id was provided
    if len(sys.argv) < 2:
        print("Usage: python examples/02_check_status.py <team_id>")
        print()
        print("Example:")
        print("  python examples/02_check_status.py abc123-def456-...")
        sys.exit(1)
    
    team_id = sys.argv[1]
    
    # Initialize the FastAPI client
    client = FastAPIClient(base_url="http://localhost:8000")
    
    print(f"Checking status for execution: {team_id}")
    print("-" * 60)
    
    try:
        # Get the team status
        response = await client.get_team_status(team_id)
        
        # Extract relevant fields
        topic = response.get("topic", "Unknown")
        status = response.get("status", "unknown")
        created_at = response.get("created_at", "")
        updated_at = response.get("updated_at", "")
        
        print(f"Topic: {topic}")
        print(f"Status: {status}")
        print(f"Created: {created_at}")
        if updated_at:
            print(f"Updated: {updated_at}")
        
        # Show entity count if completed
        if status == "completed":
            sachstand = response.get("sachstand", {})
            if isinstance(sachstand, dict):
                entities = sachstand.get("hasPart", [])
                entity_count = len(entities)
                print(f"Entities found: {entity_count}")
                print()
                print("✓ Execution completed successfully!")
                print(f"  Get results: python examples/03_get_results.py {team_id}")
        elif status == "running":
            print()
            print("⏳ Execution is still running...")
            print("   Check again in a few moments.")
        elif status == "pending":
            print()
            print("⏳ Execution is pending...")
            print("   Agent team will start shortly.")
        elif status == "failed":
            print()
            print("✗ Execution failed.")
            error_message = response.get("error_message", "No error details available")
            print(f"   Error: {error_message}")
        
    except Exception as e:
        print(f"✗ Error checking status: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
