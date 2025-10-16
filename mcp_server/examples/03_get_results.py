#!/usr/bin/env python3
"""Example script to retrieve execution results.

This script demonstrates how to retrieve the full JSON-LD results
from a completed agent team execution.

Usage:
    python examples/03_get_results.py <team_id>
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import mcp_server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.fastapi_client import FastAPIClient


async def main():
    """Retrieve results from a completed execution."""
    # Check if team_id was provided
    if len(sys.argv) < 2:
        print("Usage: python examples/03_get_results.py <team_id>")
        print()
        print("Example:")
        print("  python examples/03_get_results.py abc123-def456-...")
        sys.exit(1)
    
    team_id = sys.argv[1]
    
    # Initialize the FastAPI client
    client = FastAPIClient(base_url="http://localhost:8000")
    
    print(f"Retrieving results for execution: {team_id}")
    print("-" * 60)
    
    try:
        # First check if execution is completed
        status_response = await client.get_team_status(team_id)
        status = status_response.get("status", "unknown")
        
        if status != "completed":
            print(f"✗ Execution is not completed yet (status: {status})")
            print()
            print("Please wait for the execution to complete, then try again.")
            print(f"  Check status: python examples/02_check_status.py {team_id}")
            sys.exit(1)
        
        # Get the sachstand (results)
        response = await client.get_sachstand(team_id)
        sachstand = response.get("content")
        
        if not sachstand:
            print("✗ No results available for this execution")
            sys.exit(1)
        
        # Display summary
        topic = sachstand.get("about", {}).get("name", "Unknown")
        entities = sachstand.get("hasPart", [])
        entity_count = len(entities)
        
        print(f"Topic: {topic}")
        print(f"Entities found: {entity_count}")
        print()
        
        # Display entity breakdown by type
        entity_types = {}
        for entity in entities:
            entity_type = entity.get("@type", "Unknown")
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print("Entity breakdown:")
        for entity_type, count in sorted(entity_types.items()):
            print(f"  {entity_type}: {count}")
        print()
        
        # Display first few entities as examples
        print("Sample entities:")
        for i, entity in enumerate(entities[:3], 1):
            entity_type = entity.get("@type", "Unknown")
            name = entity.get("name", "Unnamed")
            description = entity.get("description", "No description")
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."
            print(f"  {i}. [{entity_type}] {name}")
            print(f"     {description}")
            print()
        
        if entity_count > 3:
            print(f"  ... and {entity_count - 3} more entities")
            print()
        
        # Optionally save to file
        output_file = f"results_{team_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sachstand, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Full results saved to: {output_file}")
        
    except Exception as e:
        print(f"✗ Error retrieving results: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
