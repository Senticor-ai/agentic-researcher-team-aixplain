#!/usr/bin/env python3
"""Test Inspector configuration"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from api.team_config import TeamConfig

print("\n" + "="*80)
print("TESTING INSPECTOR CONFIGURATION")
print("="*80)

try:
    # Create a test team
    print("\nCreating team with Inspector...")
    team = TeamConfig.create_team(
        topic="Test Topic for Inspector",
        goals=["Test goal"],
        enable_validation=True,
        enable_wikipedia=True,
        enable_ontology=True
    )
    
    print(f"✅ Team created successfully: {team.id}")
    print(f"✅ Team name: {team.name}")
    
    # Check if inspectors are configured
    if hasattr(team, 'inspectors'):
        print(f"✅ Inspectors attribute exists")
        print(f"   Number of inspectors: {len(team.inspectors) if team.inspectors else 0}")
    else:
        print("⚠️  No inspectors attribute found")
    
    print("\n" + "="*80)
    print("✅ Inspector configuration test complete!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
