"""
Test entity processing directly
"""
from api.entity_processor import EntityProcessor

# Simulate agent response with intermediate steps
agent_response = {
    "data": {
        "intermediate_steps": [
            {
                "agent": "Search Agent",
                "output": {
                    "entities": [
                        {
                            "type": "Person",
                            "name": "Test Person",
                            "description": "A test person",
                            "sources": [
                                {
                                    "url": "https://example.com",
                                    "excerpt": "Test excerpt"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    },
    "output": "Some markdown formatted output"
}

print("Testing EntityProcessor.receive_entities_from_agent...")
result = EntityProcessor.receive_entities_from_agent(agent_response)
print(f"Result: {result}")
print(f"Number of entities: {len(result.get('entities', []))}")

if result.get("entities"):
    print("✓ Successfully extracted entities from intermediate steps")
else:
    print("✗ Failed to extract entities")
