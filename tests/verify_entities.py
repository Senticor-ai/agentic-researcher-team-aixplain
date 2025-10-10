"""
Quick verification that entities are being extracted
"""
import requests
import json

# Get the latest team
response = requests.get("http://localhost:8000/api/v1/agent-teams")
teams = response.json()

if not teams:
    print("No teams found")
    exit(1)

# Get the most recent completed team
latest_team = teams[0]
team_id = latest_team["team_id"]

print(f"Checking team: {team_id}")
print(f"Topic: {latest_team['topic']}")
print(f"Status: {latest_team['status']}")

# Get full details
response = requests.get(f"http://localhost:8000/api/v1/agent-teams/{team_id}")
team_data = response.json()

# Check intermediate steps for Search Agent output
if "agent_response" in team_data and "data" in team_data["agent_response"]:
    intermediate_steps = team_data["agent_response"]["data"].get("intermediate_steps", [])
    
    print(f"\nFound {len(intermediate_steps)} intermediate steps")
    
    for step in intermediate_steps:
        if step.get("agent") == "Search Agent":
            print("\n=== Search Agent Output ===")
            output = step.get("output")
            print(f"Output type: {type(output)}")
            
            if isinstance(output, dict):
                entities = output.get("entities", [])
                print(f"\nExtracted {len(entities)} entities:")
                for entity in entities:
                    print(f"  - {entity.get('type')}: {entity.get('name')}")
            elif isinstance(output, str):
                print(f"Output (first 500 chars): {output[:500]}")
                # Try to parse as JSON
                try:
                    parsed = json.loads(output)
                    entities = parsed.get("entities", [])
                    print(f"\nParsed {len(entities)} entities:")
                    for entity in entities:
                        print(f"  - {entity.get('type')}: {entity.get('name')}")
                except:
                    print("Could not parse as JSON")

# Check sachstand
sachstand = team_data.get("sachstand", {})
entities_in_sachstand = sachstand.get("hasPart", [])
print(f"\n=== Sachstand ===")
print(f"Entities in Sachstand: {len(entities_in_sachstand)}")
for entity in entities_in_sachstand:
    print(f"  - {entity.get('@type')}: {entity.get('name')}")

if len(entities_in_sachstand) == 0:
    print("\n⚠ WARNING: No entities in Sachstand despite Search Agent extracting them!")
    print("This means EntityProcessor is not parsing the agent output correctly.")
