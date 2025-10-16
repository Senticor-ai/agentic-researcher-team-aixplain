#!/usr/bin/env python3
"""Complete workflow example for the MCP server.

This script demonstrates the full workflow:
1. Spawn an agent team
2. Poll for completion
3. Retrieve results
4. Display summary

Usage:
    python examples/00_full_workflow.py [topic]
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import mcp_server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.fastapi_client import FastAPIClient


async def wait_for_completion(client: FastAPIClient, team_id: str, poll_interval: int = 10, max_wait: int = 300):
    """Poll for execution completion.
    
    Args:
        client: FastAPI client instance
        team_id: Team ID to monitor
        poll_interval: Seconds between status checks (default: 10)
        max_wait: Maximum seconds to wait (default: 300 = 5 minutes)
    
    Returns:
        Final status response
    """
    elapsed = 0
    
    while elapsed < max_wait:
        response = await client.get_team_status(team_id)
        status = response.get("status")
        
        if status == "completed":
            return response
        elif status == "failed":
            error_message = response.get("error_message", "Unknown error")
            raise Exception(f"Execution failed: {error_message}")
        
        print(f"  Status: {status} (elapsed: {elapsed}s)")
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    
    raise TimeoutError(f"Execution did not complete within {max_wait} seconds")


async def main():
    """Run the complete workflow."""
    # Get topic from command line or use default
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Kinderarmut in Deutschland"
    
    # Initialize the FastAPI client
    client = FastAPIClient(base_url="http://localhost:8000")
    
    print("=" * 70)
    print("OSINT Agent Team - Complete Workflow Example")
    print("=" * 70)
    print()
    
    # Step 1: Spawn agent team
    print(f"Step 1: Spawning agent team for topic: '{topic}'")
    print("-" * 70)
    
    try:
        response = await client.create_team(
            topic=topic,
            goals=[
                "Identify key stakeholders and organizations",
                "Find relevant policies and legislation",
                "Locate expert researchers and officials"
            ],
            interaction_limit=50
        )
        
        team_id = response["team_id"]
        print(f"✓ Agent team spawned successfully!")
        print(f"  Team ID: {team_id}")
        print()
        
    except Exception as e:
        print(f"✗ Error spawning agent team: {e}")
        sys.exit(1)
    
    # Step 2: Wait for completion
    print("Step 2: Waiting for execution to complete...")
    print("-" * 70)
    print("  This typically takes 1-2 minutes.")
    print()
    
    try:
        final_status = await wait_for_completion(client, team_id, poll_interval=10)
        print(f"✓ Execution completed!")
        print()
        
    except TimeoutError as e:
        print(f"✗ Timeout: {e}")
        print(f"  You can check status later with:")
        print(f"    python examples/02_check_status.py {team_id}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        sys.exit(1)
    
    # Step 3: Retrieve results
    print("Step 3: Retrieving results...")
    print("-" * 70)
    
    try:
        response = await client.get_sachstand(team_id)
        sachstand = response.get("content")
        
        if not sachstand:
            print("✗ No results available")
            sys.exit(1)
        
        print(f"✓ Results retrieved successfully!")
        print()
        
    except Exception as e:
        print(f"✗ Error retrieving results: {e}")
        sys.exit(1)
    
    # Step 4: Display summary
    print("Step 4: Results Summary")
    print("=" * 70)
    print()
    
    # Extract summary information
    topic_name = sachstand.get("about", {}).get("name", topic)
    entities = sachstand.get("hasPart", [])
    entity_count = len(entities)
    date_created = sachstand.get("dateCreated", "Unknown")
    
    print(f"Topic: {topic_name}")
    print(f"Date: {date_created}")
    print(f"Total entities: {entity_count}")
    print()
    
    # Entity breakdown by type
    entity_types = {}
    for entity in entities:
        entity_type = entity.get("@type", "Unknown")
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    print("Entity breakdown:")
    for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {entity_type}: {count}")
    print()
    
    # Display sample entities
    print("Sample entities:")
    print()
    
    for i, entity in enumerate(entities[:5], 1):
        entity_type = entity.get("@type", "Unknown")
        name = entity.get("name", "Unnamed")
        description = entity.get("description", "No description")
        
        # Truncate long descriptions
        if len(description) > 150:
            description = description[:147] + "..."
        
        print(f"{i}. [{entity_type}] {name}")
        print(f"   {description}")
        
        # Show sources count
        sources = entity.get("sources", [])
        if sources:
            print(f"   Sources: {len(sources)}")
        
        # Show Wikidata ID if available
        wikidata_id = entity.get("wikidata_id")
        if wikidata_id:
            print(f"   Wikidata: https://www.wikidata.org/wiki/{wikidata_id}")
        
        print()
    
    if entity_count > 5:
        print(f"... and {entity_count - 5} more entities")
        print()
    
    # Save to file
    output_file = f"results_{team_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sachstand, f, indent=2, ensure_ascii=False)
    
    print("-" * 70)
    print(f"✓ Full results saved to: {output_file}")
    print()
    print("Next steps:")
    print(f"  - View results: cat {output_file}")
    print(f"  - Check status: python examples/02_check_status.py {team_id}")
    print(f"  - List all: python examples/04_list_executions.py")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
