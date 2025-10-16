#!/usr/bin/env python3
"""Example script to list executions.

This script demonstrates how to list and filter historical
agent team executions.

Usage:
    python examples/04_list_executions.py [options]
    
Options:
    --topic <filter>     Filter by topic substring
    --status <status>    Filter by status (pending, running, completed, failed)
    --limit <n>          Maximum number of results (default: 10)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import mcp_server modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.fastapi_client import FastAPIClient


def parse_args():
    """Parse command line arguments."""
    args = {
        "topic_filter": None,
        "status_filter": None,
        "limit": 10
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--topic" and i + 1 < len(sys.argv):
            args["topic_filter"] = sys.argv[i + 1]
            i += 2
        elif arg == "--status" and i + 1 < len(sys.argv):
            args["status_filter"] = sys.argv[i + 1]
            i += 2
        elif arg == "--limit" and i + 1 < len(sys.argv):
            args["limit"] = int(sys.argv[i + 1])
            i += 2
        elif arg in ["-h", "--help"]:
            print("Usage: python examples/04_list_executions.py [options]")
            print()
            print("Options:")
            print("  --topic <filter>     Filter by topic substring")
            print("  --status <status>    Filter by status (pending, running, completed, failed)")
            print("  --limit <n>          Maximum number of results (default: 10)")
            print()
            print("Examples:")
            print("  python examples/04_list_executions.py")
            print("  python examples/04_list_executions.py --status completed")
            print("  python examples/04_list_executions.py --topic climate --limit 5")
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
    
    return args


async def main():
    """List agent team executions with optional filtering."""
    # Parse command line arguments
    args = parse_args()
    
    # Initialize the FastAPI client
    client = FastAPIClient(base_url="http://localhost:8000")
    
    print("Listing executions")
    if args["topic_filter"]:
        print(f"  Topic filter: {args['topic_filter']}")
    if args["status_filter"]:
        print(f"  Status filter: {args['status_filter']}")
    print(f"  Limit: {args['limit']}")
    print("-" * 60)
    
    try:
        # List teams with filters
        teams = await client.list_teams(
            topic_filter=args["topic_filter"],
            status_filter=args["status_filter"],
            limit=args["limit"]
        )
        
        if not teams:
            print("No executions found matching the criteria.")
            return
        
        print(f"Found {len(teams)} execution(s):\n")
        
        # Display each execution
        for i, team in enumerate(teams, 1):
            team_id = team.get("team_id", "Unknown")
            topic = team.get("topic", "Unknown")
            status = team.get("status", "unknown")
            created_at = team.get("created_at", "")
            
            # Status emoji
            status_emoji = {
                "pending": "⏳",
                "running": "▶️",
                "completed": "✓",
                "failed": "✗"
            }.get(status, "?")
            
            print(f"{i}. {status_emoji} {topic}")
            print(f"   ID: {team_id}")
            print(f"   Status: {status}")
            print(f"   Created: {created_at}")
            
            # Show entity count if completed
            if status == "completed":
                sachstand = team.get("sachstand", {})
                if isinstance(sachstand, dict):
                    entities = sachstand.get("hasPart", [])
                    entity_count = len(entities)
                    print(f"   Entities: {entity_count}")
            
            print()
        
        print("Commands:")
        print("  Check status: python examples/02_check_status.py <team_id>")
        print("  Get results:  python examples/03_get_results.py <team_id>")
        
    except Exception as e:
        print(f"✗ Error listing executions: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
