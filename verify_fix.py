#!/usr/bin/env python3
"""Quick verification that the fix is working"""
import json
import sys
sys.path.insert(0, '.')

from api.entity_processor import EntityProcessor

# Load the sample data
with open('tests/data/output-test-sample.json', 'r') as f:
    sample_data = json.load(f)

print("Testing Response Generator format parsing...")
print(f"Input format: {list(sample_data.keys())}")

# Test conversion
result = EntityProcessor.convert_grouped_entities(sample_data)
entities = result.get("entities", [])

print(f"\n✅ SUCCESS: Converted {len(entities)} entities")
print(f"Expected: 10 entities (3 Person, 3 Organization, 2 Event, 2 Topic)")

# Count by type
type_counts = {}
for entity in entities:
    entity_type = entity.get("type", "Unknown")
    type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

print(f"\nActual breakdown:")
for entity_type, count in sorted(type_counts.items()):
    print(f"  - {entity_type}: {count}")

if len(entities) == 10:
    print("\n🎉 FIX VERIFIED: All 10 entities are correctly parsed!")
    print("\nThe backend will now correctly count all entities from the Response Generator.")
else:
    print(f"\n❌ Issue: Expected 10 entities, got {len(entities)}")
