"""
Demo: Ontology Agent Suggestions

This demo shows how the Ontology Agent can suggest improvements to entities.
It creates sample entities and demonstrates the types of suggestions the agent would make.
"""
import json
from api.team_config import TeamConfig
from api.instructions.ontology_agent import get_ontology_agent_instructions


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_ontology_agent_instructions():
    """Demo: Show Ontology Agent instructions"""
    print_section("ONTOLOGY AGENT INSTRUCTIONS")
    
    instructions = get_ontology_agent_instructions()
    
    # Show key sections
    print("\n📋 Key Capabilities:")
    print("  • Suggests more specific schema.org types")
    print("  • Identifies relationships between entities")
    print("  • Recommends additional properties")
    print("  • Ensures semantic consistency")
    
    print(f"\n📏 Instructions length: {len(instructions)} characters")
    
    # Show excerpt
    print("\n📝 Instructions excerpt:")
    excerpt_start = instructions.find("Your role is")
    excerpt_end = instructions.find("AUTONOMOUS BEHAVIOR:")
    if excerpt_start != -1 and excerpt_end != -1:
        excerpt = instructions[excerpt_start:excerpt_end].strip()
        print(f"\n{excerpt[:300]}...")


def demo_sample_entities():
    """Demo: Show sample entities that could benefit from ontology improvements"""
    print_section("SAMPLE ENTITIES FOR IMPROVEMENT")
    
    sample_entities = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit",
            "description": "German federal ministry responsible for environmental protection"
        },
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Dr. Manfred Lucha",
            "description": "Minister für Soziales, Gesundheit und Integration Baden-Württemberg"
        },
        {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": "Klimagipfel 2024",
            "description": "Annual climate summit in Stuttgart"
        }
    ]
    
    for i, entity in enumerate(sample_entities, 1):
        print(f"\n{i}. {entity['name']}")
        print(f"   Current Type: {entity['@type']}")
        print(f"   Description: {entity['description']}")


def demo_type_improvements():
    """Demo: Show type improvement suggestions"""
    print_section("TYPE IMPROVEMENT SUGGESTIONS")
    
    improvements = [
        {
            "entity": "Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit",
            "current_type": "Organization",
            "suggested_type": "GovernmentOrganization",
            "reason": "This is a federal government ministry. GovernmentOrganization is more specific and better represents government entities.",
            "reference": "https://schema.org/GovernmentOrganization"
        },
        {
            "entity": "Dr. Manfred Lucha",
            "current_type": "Person",
            "suggested_type": "Person",
            "additional_property": "jobTitle",
            "suggested_value": "Minister für Soziales, Gesundheit und Integration",
            "reason": "Person type is appropriate, but adding jobTitle property makes the role explicit and machine-readable.",
            "reference": "https://schema.org/jobTitle"
        },
        {
            "entity": "Klimagipfel 2024",
            "current_type": "Event",
            "suggested_type": "ConferenceEvent",
            "reason": "This is a conference/summit. ConferenceEvent is more specific than generic Event type.",
            "reference": "https://schema.org/ConferenceEvent"
        }
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"\n{i}. Entity: {improvement['entity']}")
        print(f"   Current Type: {improvement['current_type']}")
        
        if improvement.get('suggested_type') != improvement['current_type']:
            print(f"   → Suggested Type: {improvement['suggested_type']}")
        
        if improvement.get('additional_property'):
            print(f"   → Add Property: {improvement['additional_property']}")
            print(f"   → Value: {improvement['suggested_value']}")
        
        print(f"   Reason: {improvement['reason']}")
        print(f"   Reference: {improvement['reference']}")


def demo_relationship_suggestions():
    """Demo: Show relationship suggestions"""
    print_section("RELATIONSHIP SUGGESTIONS")
    
    relationships = [
        {
            "entity1": "Dr. Manfred Lucha",
            "entity2": "Ministerium für Soziales, Gesundheit und Integration Baden-Württemberg",
            "property": "worksFor",
            "reason": "Explicitly connects the minister to their ministry, making organizational structure machine-readable.",
            "reference": "https://schema.org/worksFor"
        },
        {
            "entity1": "Ministerium für Umwelt Baden-Württemberg",
            "entity2": "Landesregierung Baden-Württemberg",
            "property": "parentOrganization",
            "reason": "Shows the ministry is part of the state government, enabling hierarchical queries.",
            "reference": "https://schema.org/parentOrganization"
        },
        {
            "entity1": "Klimagipfel 2024",
            "entity2": "Ministerium für Umwelt",
            "property": "organizer",
            "reason": "Links the event to its organizing entity, making event relationships explicit.",
            "reference": "https://schema.org/organizer"
        }
    ]
    
    for i, rel in enumerate(relationships, 1):
        print(f"\n{i}. Relationship:")
        print(f"   {rel['entity1']}")
        print(f"   → {rel['property']} →")
        print(f"   {rel['entity2']}")
        print(f"   Reason: {rel['reason']}")
        print(f"   Reference: {rel['reference']}")


def demo_improved_entities():
    """Demo: Show entities after applying ontology improvements"""
    print_section("ENTITIES AFTER ONTOLOGY IMPROVEMENTS")
    
    improved_entities = [
        {
            "@context": "https://schema.org",
            "@type": "GovernmentOrganization",
            "name": "Bundesministerium für Umwelt, Naturschutz und nukleare Sicherheit",
            "alternateName": "BMU",
            "description": "German federal ministry responsible for environmental protection",
            "parentOrganization": {
                "@type": "GovernmentOrganization",
                "name": "Bundesregierung Deutschland"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Dr. Manfred Lucha",
            "jobTitle": "Minister für Soziales, Gesundheit und Integration",
            "description": "Minister für Soziales, Gesundheit und Integration Baden-Württemberg",
            "worksFor": {
                "@type": "GovernmentOrganization",
                "name": "Ministerium für Soziales, Gesundheit und Integration Baden-Württemberg"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "ConferenceEvent",
            "name": "Klimagipfel 2024",
            "description": "Annual climate summit in Stuttgart",
            "startDate": "2024-03-15",
            "location": {
                "@type": "Place",
                "name": "Stuttgart"
            },
            "organizer": {
                "@type": "GovernmentOrganization",
                "name": "Ministerium für Umwelt Baden-Württemberg"
            }
        }
    ]
    
    for i, entity in enumerate(improved_entities, 1):
        print(f"\n{i}. {entity['name']}")
        print(f"   Type: {entity['@type']} ✓")
        
        if 'alternateName' in entity:
            print(f"   Alternate Name: {entity['alternateName']} ✓")
        
        if 'jobTitle' in entity:
            print(f"   Job Title: {entity['jobTitle']} ✓")
        
        if 'worksFor' in entity:
            print(f"   Works For: {entity['worksFor']['name']} ✓")
        
        if 'parentOrganization' in entity:
            print(f"   Parent Org: {entity['parentOrganization']['name']} ✓")
        
        if 'organizer' in entity:
            print(f"   Organizer: {entity['organizer']['name']} ✓")
        
        if 'startDate' in entity:
            print(f"   Start Date: {entity['startDate']} ✓")
        
        print(f"\n   JSON:")
        print(f"   {json.dumps(entity, indent=2, ensure_ascii=False)[:200]}...")


def demo_semantic_value():
    """Demo: Show the semantic value of ontology improvements"""
    print_section("SEMANTIC VALUE OF IMPROVEMENTS")
    
    print("\n🎯 Benefits of Ontology Improvements:")
    
    benefits = [
        {
            "improvement": "More Specific Types",
            "example": "Organization → GovernmentOrganization",
            "value": "Enables queries like 'find all government entities' and improves integration with government data systems"
        },
        {
            "improvement": "Relationship Properties",
            "example": "Person worksFor Organization",
            "value": "Makes organizational structure machine-readable, enables queries like 'who works for this ministry?'"
        },
        {
            "improvement": "Additional Properties",
            "example": "alternateName for abbreviations",
            "value": "Improves discoverability, helps users find entities using informal names or abbreviations"
        },
        {
            "improvement": "Semantic Consistency",
            "example": "All ministries use GovernmentOrganization",
            "value": "Enables consistent queries across entity pool, improves data quality and integration"
        }
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"\n{i}. {benefit['improvement']}")
        print(f"   Example: {benefit['example']}")
        print(f"   Value: {benefit['value']}")


def demo_create_ontology_agent():
    """Demo: Create Ontology Agent (requires API credentials)"""
    print_section("CREATE ONTOLOGY AGENT")
    
    try:
        print("\n🔧 Creating Ontology Agent...")
        agent = TeamConfig.create_ontology_agent()
        
        print(f"✓ Ontology Agent created successfully!")
        print(f"  Agent ID: {agent.id}")
        print(f"  Agent Name: {agent.name}")
        
        if hasattr(agent, 'description'):
            print(f"  Description: {agent.description}")
        
        print("\n📋 Agent Configuration:")
        print(f"  • Uses GPT-4o model for schema.org expertise")
        print(f"  • No external tools needed (uses built-in knowledge)")
        print(f"  • Works autonomously to monitor entity pool")
        print(f"  • Provides suggestions, doesn't enforce changes")
        
        return agent
        
    except Exception as e:
        print(f"\n⚠ Could not create Ontology Agent (may need API credentials)")
        print(f"  Error: {e}")
        return None


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  ONTOLOGY AGENT DEMONSTRATION")
    print("=" * 70)
    
    # Demo 1: Instructions
    demo_ontology_agent_instructions()
    
    # Demo 2: Sample entities
    demo_sample_entities()
    
    # Demo 3: Type improvements
    demo_type_improvements()
    
    # Demo 4: Relationship suggestions
    demo_relationship_suggestions()
    
    # Demo 5: Improved entities
    demo_improved_entities()
    
    # Demo 6: Semantic value
    demo_semantic_value()
    
    # Demo 7: Create agent (requires API)
    demo_create_ontology_agent()
    
    print("\n" + "=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n✓ Ontology Agent can suggest schema.org improvements")
    print("✓ Suggestions include type improvements and relationships")
    print("✓ Improvements add semantic richness and machine-readability")
    print("✓ Agent works autonomously as part of the hive mind")
    print()


if __name__ == "__main__":
    main()
