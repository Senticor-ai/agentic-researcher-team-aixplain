#!/usr/bin/env python3
"""Example script to spawn an agent team.

This script demonstrates how to use the FastAPI backend directly
to spawn an agent team for topic research.

Usage:
    python examples/01_spawn_agent_team.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import mcp_server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.fastapi_client import FastAPIClient


async def main():
    """Spawn an agent team for a sample topic."""
    # Initialize the FastAPI client
    # Change this URL if your backend is running on a different host/port
    client = FastAPIClient(base_url="http://localhost:8000")
    
    # Define the research topic and parameters
    topic = "Kinderarmut in Deutschland"
    goals = [
        "Identify key statistics and trends",
        "Find relevant government policies",
        "Locate expert organizations and researchers"
    ]
    interaction_limit = 50
    
    print(f"Spawning agent team for topic: '{topic}'")
    print(f"Goals: {goals}")
    print(f"Interaction limit: {interaction_limit}")
    print("-" * 60)
    
    try:
        # Spawn the agent team
        response = await client.create_team(
            topic=topic,
            goals=goals,
            interaction_limit=interaction_limit
        )
        
        # Extract the team ID
        team_id = response["team_id"]
        status = response.get("status", "pending")
        created_at = response.get("created_at", "")
        
        print(f"✓ Agent team spawned successfully!")
        print(f"  Team ID: {team_id}")
        print(f"  Status: {status}")
        print(f"  Created: {created_at}")
        print()
        print("Next steps:")
        print(f"  1. Check status: python examples/02_check_status.py {team_id}")
        print(f"  2. Get results: python examples/03_get_results.py {team_id}")
        print()
        print("Note: Agent execution typically takes 1-2 minutes.")
        
        return team_id
        
    except Exception as e:
        print(f"✗ Error spawning agent team: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
