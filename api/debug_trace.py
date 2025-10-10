"""
Debug script to inspect agent trace data structure
Run this after creating a team to see what data is available
"""
import json
from api.storage import get_store

def inspect_trace(team_id: str):
    """Inspect the trace data for a team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        print(f"Team {team_id} not found")
        return
    
    print(f"\n{'='*80}")
    print(f"Team: {team_id}")
    print(f"Status: {team['status']}")
    print(f"{'='*80}\n")
    
    agent_response = team.get("agent_response")
    if not agent_response:
        print("No agent_response available yet")
        return
    
    print("Agent Response Keys:")
    print(json.dumps(list(agent_response.keys()), indent=2))
    print()
    
    intermediate_steps = agent_response.get("intermediate_steps", [])
    print(f"Intermediate Steps Count: {len(intermediate_steps)}")
    print()
    
    for idx, step in enumerate(intermediate_steps):
        print(f"\n{'-'*80}")
        print(f"Step {idx + 1}")
        print(f"{'-'*80}")
        print(f"Type: {type(step)}")
        
        if isinstance(step, dict):
            print(f"Keys: {list(step.keys())}")
            print("\nStep Data:")
            print(json.dumps(step, indent=2, default=str))
        elif isinstance(step, str):
            print(f"String Length: {len(step)}")
            print(f"Preview: {step[:200]}...")
        else:
            print(f"Raw: {step}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m api.debug_trace <team_id>")
        print("\nAvailable teams:")
        store = get_store()
        teams = store.get_all_teams()
        for team in teams:
            print(f"  - {team['team_id']} ({team['status']}): {team['topic']}")
        sys.exit(1)
    
    team_id = sys.argv[1]
    inspect_trace(team_id)
