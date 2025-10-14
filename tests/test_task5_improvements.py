"""
Test to verify Task 5 improvements to Mentalist instructions
This test runs a research query and checks if the enhanced instructions
lead to better entity extraction results.
"""
import requests
import json
import time

API_BASE = "http://localhost:8080/api/v1"

def test_enhanced_mentalist_instructions():
    """
    Test that enhanced Mentalist instructions lead to:
    1. More diverse entity types (not just Person/Organization)
    2. Multiple search rounds
    3. Better coverage
    """
    
    print("\n" + "="*70)
    print("TESTING TASK 5: Enhanced Mentalist Instructions")
    print("="*70)
    
    # Use a topic that should yield diverse entity types
    topic = "Jugendarmut Baden-Württemberg 2025"
    
    print(f"\n📋 Topic: {topic}")
    print(f"🎯 Expected improvements:")
    print(f"   - Multiple entity types (Person, Organization, Topic, Event, Policy)")
    print(f"   - Multiple search rounds with different strategies")
    print(f"   - At least 10+ entities extracted")
    print(f"   - Diverse sources")
    
    # Create agent team
    response = requests.post(
        f"{API_BASE}/agent-teams",
        json={
            "topic": topic,
            "goals": [
                "Find key policies and regulations",
                "Identify important events and deadlines",
                "Locate relevant topics and themes",
                "Find organizations and officials involved"
            ]
        }
    )
    
    if response.status_code != 200:
        print(f"\n❌ Error creating team: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    team_id = data["team_id"]
    print(f"\n✅ Created team: {team_id}")
    
    # Wait for completion (max 5 minutes for thorough research)
    max_wait = 300
    start_time = time.time()
    last_status = None
    
    print("\n⏳ Waiting for research to complete...")
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{API_BASE}/agent-teams/{team_id}")
        if response.status_code != 200:
            print(f"\n❌ Error getting team: {response.status_code}")
            return False
        
        team_data = response.json()
        status = team_data["status"]
        
        if status != last_status:
            print(f"   Status: {status}")
            last_status = status
        
        if status == "completed":
            elapsed = time.time() - start_time
            print(f"\n✅ Research completed in {elapsed:.1f} seconds")
            break
        elif status == "failed":
            print("\n❌ Research failed")
            print(f"Execution log:")
            for log in team_data.get("execution_log", []):
                print(f"  - {log}")
            return False
        
        time.sleep(3)
    else:
        print(f"\n⚠️  Research did not complete within {max_wait}s timeout")
        return False
    
    # Analyze results
    print("\n" + "="*70)
    print("RESULTS ANALYSIS")
    print("="*70)
    
    sachstand = team_data.get("sachstand", {})
    entities = sachstand.get("hasPart", [])
    
    print(f"\n📊 Total entities extracted: {len(entities)}")
    
    # Count by type
    entity_types = {}
    for entity in entities:
        entity_type = entity.get("@type", "Unknown")
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    print(f"\n📈 Entity type distribution:")
    for entity_type, count in sorted(entity_types.items()):
        print(f"   {entity_type}: {count}")
    
    # Check for diverse entity types
    has_person = entity_types.get("Person", 0) > 0
    has_org = entity_types.get("Organization", 0) > 0
    has_topic = entity_types.get("Topic", 0) > 0
    has_event = entity_types.get("Event", 0) > 0
    has_policy = entity_types.get("Policy", 0) > 0
    
    diversity_score = sum([has_person, has_org, has_topic, has_event, has_policy])
    
    print(f"\n✨ Entity type diversity: {diversity_score}/5 types")
    print(f"   {'✅' if has_person else '❌'} Person entities")
    print(f"   {'✅' if has_org else '❌'} Organization entities")
    print(f"   {'✅' if has_topic else '❌'} Topic entities")
    print(f"   {'✅' if has_event else '❌'} Event entities")
    print(f"   {'✅' if has_policy else '❌'} Policy entities")
    
    # Check source diversity
    all_sources = set()
    for entity in entities:
        for citation in entity.get("citation", []):
            url = citation.get("url", "")
            if url:
                all_sources.add(url)
    
    print(f"\n🌐 Unique sources: {len(all_sources)}")
    
    # Show sample entities from each type
    print(f"\n📋 Sample entities:")
    for entity_type in ["Person", "Organization", "Topic", "Event", "Policy"]:
        samples = [e for e in entities if e.get("@type") == entity_type][:2]
        if samples:
            print(f"\n   {entity_type}:")
            for entity in samples:
                name = entity.get("name", "Unknown")
                desc = entity.get("description", "")
                if desc and len(desc) > 80:
                    desc = desc[:80] + "..."
                print(f"      • {name}")
                if desc:
                    print(f"        {desc}")
    
    # Success criteria
    print("\n" + "="*70)
    print("SUCCESS CRITERIA")
    print("="*70)
    
    criteria_met = []
    criteria_failed = []
    
    # Criterion 1: At least 10 entities
    if len(entities) >= 10:
        criteria_met.append(f"✅ Extracted {len(entities)} entities (≥10 required)")
    else:
        criteria_failed.append(f"❌ Only {len(entities)} entities (≥10 required)")
    
    # Criterion 2: At least 3 entity types
    if diversity_score >= 3:
        criteria_met.append(f"✅ {diversity_score} entity types (≥3 required)")
    else:
        criteria_failed.append(f"❌ Only {diversity_score} entity types (≥3 required)")
    
    # Criterion 3: Has Topic or Event entities (new types)
    if has_topic or has_event or has_policy:
        new_types = []
        if has_topic:
            new_types.append(f"Topic({entity_types.get('Topic', 0)})")
        if has_event:
            new_types.append(f"Event({entity_types.get('Event', 0)})")
        if has_policy:
            new_types.append(f"Policy({entity_types.get('Policy', 0)})")
        criteria_met.append(f"✅ New entity types found: {', '.join(new_types)}")
    else:
        criteria_failed.append(f"❌ No new entity types (Topic/Event/Policy) found")
    
    # Criterion 4: Diverse sources
    if len(all_sources) >= 5:
        criteria_met.append(f"✅ {len(all_sources)} unique sources (≥5 required)")
    else:
        criteria_failed.append(f"❌ Only {len(all_sources)} sources (≥5 required)")
    
    print()
    for criterion in criteria_met:
        print(criterion)
    for criterion in criteria_failed:
        print(criterion)
    
    # Overall assessment
    success = len(criteria_failed) == 0
    
    print("\n" + "="*70)
    if success:
        print("🎉 SUCCESS: Enhanced instructions are working well!")
        print("="*70)
        print("\nThe multi-round search strategy and feedback loops are")
        print("producing more comprehensive and diverse entity extraction.")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Some criteria not met")
        print("="*70)
        print("\nConsider:")
        print("- Checking if the Mentalist is using all search rounds")
        print("- Verifying the Search Agent is extracting all entity types")
        print("- Ensuring sufficient interaction budget is available")
    
    # Save detailed results
    output_file = f"output/task5_test_{team_id}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "team_id": team_id,
            "topic": topic,
            "total_entities": len(entities),
            "entity_types": entity_types,
            "diversity_score": diversity_score,
            "unique_sources": len(all_sources),
            "criteria_met": criteria_met,
            "criteria_failed": criteria_failed,
            "success": success,
            "sachstand": sachstand
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print()
    
    return success

if __name__ == "__main__":
    success = test_enhanced_mentalist_instructions()
    exit(0 if success else 1)
