"""
Test entity extraction with Jugendarmut Baden-Württemberg 2025
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

print("=== Testing: Jugendarmut Baden-Württemberg 2025 ===\n")

# Create agent team
response = requests.post(
    f"{API_BASE}/agent-teams",
    json={
        "topic": "Jugendarmut Baden-Württemberg 2025",
        "goals": [
            "Find key organizations working on youth poverty",
            "Identify government officials and experts",
            "Locate relevant statistics and reports",
            "Find web links to authoritative sources"
        ]
    }
)

if response.status_code != 200:
    print(f"Error creating team: {response.status_code}")
    exit(1)

data = response.json()
team_id = data["team_id"]
print(f"Created team: {team_id}\n")

# Wait for completion (max 3 minutes)
max_wait = 180
start_time = time.time()

while time.time() - start_time < max_wait:
    response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
    if response.status_code != 200:
        print(f"Error getting team: {response.status_code}")
        exit(1)
    
    team_data = response.json()
    status = team_data["status"]
    print(f"Status: {status}")
    
    if status == "completed":
        print("\n✓ Team completed successfully\n")
        break
    elif status == "failed":
        print("\n✗ Team failed")
        print(f"Execution log:")
        for log in team_data.get("execution_log", []):
            print(f"  - {log}")
        exit(1)
    
    time.sleep(5)
else:
    print("\n⚠ Team did not complete within timeout")
    exit(1)

# Display results
sachstand = team_data.get("sachstand", {})
entities = sachstand.get("hasPart", [])

print("=" * 60)
print(f"RESULTS: Extracted {len(entities)} entities")
print("=" * 60)

if entities:
    # Group by type
    people = [e for e in entities if e.get("@type") == "Person"]
    orgs = [e for e in entities if e.get("@type") == "Organization"]
    
    if people:
        print(f"\n📋 PEOPLE ({len(people)}):")
        for person in people:
            print(f"\n  👤 {person.get('name')}")
            if person.get("description"):
                print(f"     {person.get('description')}")
            if person.get("jobTitle"):
                print(f"     Role: {person.get('jobTitle')}")
            sources = person.get("citation", [])
            if sources:
                print(f"     🔗 Sources: {len(sources)}")
                for source in sources[:2]:  # Show first 2 sources
                    print(f"        - {source.get('url')}")
    
    if orgs:
        print(f"\n🏢 ORGANIZATIONS ({len(orgs)}):")
        for org in orgs:
            print(f"\n  🏛️  {org.get('name')}")
            if org.get("description"):
                print(f"     {org.get('description')}")
            sources = org.get("citation", [])
            if sources:
                print(f"     🔗 Sources: {len(sources)}")
                for source in sources[:2]:  # Show first 2 sources
                    print(f"        - {source.get('url')}")
    
    # Show all unique source URLs
    all_sources = set()
    for entity in entities:
        for citation in entity.get("citation", []):
            all_sources.add(citation.get("url"))
    
    print(f"\n🌐 ALL SOURCE LINKS ({len(all_sources)}):")
    for url in sorted(all_sources):
        print(f"  - {url}")
    
    # Save to file
    output_file = f"output/sachstand_{team_id}.jsonld"
    print(f"\n💾 Full JSON-LD saved to: {output_file}")
    
else:
    print("\n⚠ No entities extracted")
    print("\nThis could mean:")
    print("  - Topic is too specific or niche")
    print("  - Limited information available in English sources")
    print("  - Search results didn't contain clear entity mentions")
    print("\nTip: Try broader topics or topics with more international coverage")

print("\n" + "=" * 60)
