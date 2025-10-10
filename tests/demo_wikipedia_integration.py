"""
Demo script to show Wikipedia integration capabilities

This script demonstrates how Wikipedia enrichment works by:
1. Showing the team configuration with Wikipedia agent
2. Demonstrating entity enrichment with mock data
3. Showing the JSON-LD output with Wikipedia links
"""
import json
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables BEFORE importing aixplain
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Verify API key is loaded
if not os.getenv("TEAM_API_KEY"):
    print("ERROR: TEAM_API_KEY not found in environment")
    print(f"Tried to load from: {env_path}")
    sys.exit(1)

from api.team_config import TeamConfig
from api.entity_processor import EntityProcessor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def demo_wikipedia_configuration():
    """Demonstrate Wikipedia agent configuration"""
    print("\n" + "="*80)
    print("DEMO 1: Wikipedia Agent Configuration")
    print("="*80)
    
    # Check if Wikipedia tool is configured
    wikipedia_tool_id = TeamConfig.TOOL_IDS.get("wikipedia")
    
    if wikipedia_tool_id:
        print(f"✓ Wikipedia tool configured: {wikipedia_tool_id}")
    else:
        print("✗ Wikipedia tool NOT configured (set to None)")
        print("  To enable Wikipedia enrichment:")
        print("  1. Get Wikipedia tool ID from aixplain marketplace")
        print("  2. Update api/team_config.py TOOL_IDS['wikipedia']")
        print("  3. See docs/WIKIPEDIA_TOOL_SETUP.md for details")
    
    # Try to create Wikipedia agent
    print("\nAttempting to create Wikipedia agent...")
    wikipedia_agent = TeamConfig.create_wikipedia_agent(model="testing")
    
    if wikipedia_agent:
        print(f"✓ Wikipedia agent created: {wikipedia_agent.name}")
        print(f"  Agent ID: {wikipedia_agent.id}")
    else:
        print("✗ Wikipedia agent not created (tool not configured)")


def demo_team_with_wikipedia():
    """Demonstrate team creation with Wikipedia agent"""
    print("\n" + "="*80)
    print("DEMO 2: Team Creation with Wikipedia Agent")
    print("="*80)
    
    topic = "Dr. Manfred Lucha Baden-Württemberg"
    goals = ["Find biographical information", "Identify official roles"]
    
    print(f"\nTopic: {topic}")
    print(f"Goals: {goals}")
    
    # Create team with Wikipedia enabled
    print("\nCreating team with Wikipedia agent enabled...")
    team = TeamConfig.create_team(
        topic=topic,
        goals=goals,
        model="testing",
        enable_wikipedia=True
    )
    
    print(f"✓ Team created: {team.name}")
    print(f"  Team ID: {team.id}")
    
    # Show team structure
    print("\nTeam structure:")
    print("  Built-in micro agents:")
    print("    - Mentalist (strategic planner)")
    print("    - Inspector (quality monitor)")
    print("    - Orchestrator (agent spawner)")
    print("    - Response Generator (output synthesizer)")
    print("  User-defined agents:")
    print("    - Search Agent (Tavily Search tool)")
    
    if TeamConfig.TOOL_IDS.get("wikipedia"):
        print("    - Wikipedia Agent (Wikipedia tool)")
    else:
        print("    - Wikipedia Agent (NOT ADDED - tool not configured)")


def demo_wikipedia_enrichment():
    """Demonstrate Wikipedia enrichment with mock data"""
    print("\n" + "="*80)
    print("DEMO 3: Wikipedia Enrichment Process")
    print("="*80)
    
    # Mock entities from Search Agent
    print("\nStep 1: Search Agent extracts entities")
    entities_data = {
        "entities": [
            {
                "type": "Person",
                "name": "Dr. Manfred Lucha",
                "description": "Minister für Soziales, Gesundheit und Integration Baden-Württemberg",
                "jobTitle": "Minister",
                "sources": [
                    {
                        "url": "https://sozialministerium.baden-wuerttemberg.de/minister",
                        "excerpt": "Minister Dr. Manfred Lucha leitet das Ministerium..."
                    }
                ]
            },
            {
                "type": "Organization",
                "name": "Ministerium für Soziales, Gesundheit und Integration Baden-Württemberg",
                "description": "State ministry responsible for social affairs, health and integration",
                "sources": [
                    {
                        "url": "https://sozialministerium.baden-wuerttemberg.de/",
                        "excerpt": "Das Ministerium ist zuständig für..."
                    }
                ]
            }
        ]
    }
    
    print(f"  Extracted {len(entities_data['entities'])} entities:")
    for entity in entities_data['entities']:
        print(f"    - {entity['type']}: {entity['name']}")
    
    # Mock Wikipedia enrichment
    print("\nStep 2: Wikipedia Agent enriches entities")
    wikipedia_data = {
        "Dr. Manfred Lucha": {
            "wikipedia_links": [
                {
                    "language": "de",
                    "url": "https://de.wikipedia.org/wiki/Manfred_Lucha",
                    "title": "Manfred Lucha"
                },
                {
                    "language": "en",
                    "url": "https://en.wikipedia.org/wiki/Manfred_Lucha",
                    "title": "Manfred Lucha"
                }
            ],
            "wikidata_id": "Q1889089",
            "sameAs": [
                "https://de.wikipedia.org/wiki/Manfred_Lucha",
                "https://en.wikipedia.org/wiki/Manfred_Lucha",
                "https://www.wikidata.org/wiki/Q1889089"
            ]
        }
    }
    
    print(f"  Enriched {len(wikipedia_data)} entities with Wikipedia data:")
    for entity_name, wiki_info in wikipedia_data.items():
        print(f"    - {entity_name}:")
        print(f"      Wikidata ID: {wiki_info['wikidata_id']}")
        print(f"      Wikipedia links: {len(wiki_info['wikipedia_links'])} languages")
        print(f"      sameAs URLs: {len(wiki_info['sameAs'])}")
    
    # Merge Wikipedia data
    print("\nStep 3: Merge Wikipedia data into entities")
    enriched_entities = EntityProcessor.merge_wikipedia_data(entities_data, wikipedia_data)
    
    print(f"  Merged Wikipedia data into {len(enriched_entities['entities'])} entities")
    for entity in enriched_entities['entities']:
        if 'wikidata_id' in entity:
            print(f"    ✓ {entity['name']} - enriched with Wikipedia data")
        else:
            print(f"    - {entity['name']} - no Wikipedia data")


def demo_jsonld_output():
    """Demonstrate JSON-LD output with Wikipedia enrichment"""
    print("\n" + "="*80)
    print("DEMO 4: JSON-LD Output with Wikipedia Enrichment")
    print("="*80)
    
    # Create entities with Wikipedia enrichment
    entities = [
        {
            "type": "Person",
            "name": "Dr. Manfred Lucha",
            "description": "Minister für Soziales, Gesundheit und Integration Baden-Württemberg",
            "jobTitle": "Minister",
            "sources": [
                {
                    "url": "https://sozialministerium.baden-wuerttemberg.de/minister",
                    "excerpt": "Minister Dr. Manfred Lucha..."
                }
            ],
            "sameAs": [
                "https://de.wikipedia.org/wiki/Manfred_Lucha",
                "https://en.wikipedia.org/wiki/Manfred_Lucha",
                "https://www.wikidata.org/wiki/Q1889089"
            ],
            "wikidata_id": "Q1889089",
            "wikipedia_links": [
                {
                    "language": "de",
                    "url": "https://de.wikipedia.org/wiki/Manfred_Lucha",
                    "title": "Manfred Lucha"
                },
                {
                    "language": "en",
                    "url": "https://en.wikipedia.org/wiki/Manfred_Lucha",
                    "title": "Manfred Lucha"
                }
            ]
        }
    ]
    
    # Generate JSON-LD
    sachstand = EntityProcessor.generate_jsonld_sachstand(
        topic="Dr. Manfred Lucha Baden-Württemberg",
        entities=entities,
        completion_status="complete"
    )
    
    print("\nGenerated JSON-LD Sachstand:")
    print(json.dumps(sachstand, indent=2, ensure_ascii=False))
    
    # Highlight Wikipedia enrichment
    print("\n" + "-"*80)
    print("Wikipedia Enrichment in JSON-LD:")
    print("-"*80)
    
    entity = sachstand["hasPart"][0]
    
    if "sameAs" in entity:
        print("\n✓ sameAs property (schema.org standard for entity linking):")
        for url in entity["sameAs"]:
            print(f"    - {url}")
    
    if "identifier" in entity:
        print("\n✓ identifier property (Wikidata ID):")
        print(f"    - Property: {entity['identifier']['propertyID']}")
        print(f"    - Value: {entity['identifier']['value']}")
    
    print("\nBenefits of Wikipedia enrichment:")
    print("  1. Authoritative references from Wikipedia")
    print("  2. Multi-language support (de, en, fr)")
    print("  3. Wikidata IDs enable entity deduplication")
    print("  4. Links to broader knowledge graphs")
    print("  5. Verification of entity notability")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("WIKIPEDIA INTEGRATION DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows how Wikipedia enrichment works in the Honeycomb OSINT system.")
    print("It demonstrates the configuration, team creation, enrichment process, and output.")
    
    try:
        demo_wikipedia_configuration()
        demo_team_with_wikipedia()
        demo_wikipedia_enrichment()
        demo_jsonld_output()
        
        print("\n" + "="*80)
        print("DEMO COMPLETE")
        print("="*80)
        print("\nNext steps:")
        print("  1. Configure Wikipedia tool ID (see docs/WIKIPEDIA_TOOL_SETUP.md)")
        print("  2. Run end-to-end test with real Wikipedia agent")
        print("  3. Test with known entities (e.g., 'Dr. Manfred Lucha')")
        print("  4. Verify Wikipedia links in JSON-LD output")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
