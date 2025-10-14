"""
Quick test with a well-documented English topic
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

print("=== Testing: Climate Policy EU 2024 ===\n")

response = requests.post(
    f"{API_BASE}/agent-teams",
    json={
        "topic": "Climate Policy EU 2024",
        "goals": [
            "Find key EU organizations working on climate policy",
            "Identify important officials and experts",
            "Locate policy documents and initiatives"
        ]
    }
)

data = response.json()
team_id = data["team_id"]
print(f"Created team: {team_id}\n")

# Wait for completion
max_wait = 120
start_time = time.time()

while time.time() - start_time < max_wait:
    response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
    team_data = response.json()
    status = team_data["status"]
    
    if status == "completed":
        print("✓ Completed\n")
        break
    elif status == "failed":
        print("✗ Failed\n")
        exit(1)
    
    time.sleep(5)

# Show results
sachstand = team_data.get("sachstand", {})
entities = sachstand.get("hasPart", [])

print(f"📊 Extracted {len(entities)} entities\n")

for entity in entities:
    print(f"  • {entity.get('@type')}: {entity.get('name')}")
    if entity.get("description"):
        print(f"    {entity.get('description')[:100]}...")

print(f"\n💾 Saved to: output/sachstand_{team_id}.jsonld")
