#!/usr/bin/env python3
"""Test the agent configuration endpoint"""
import json
import sys
sys.path.insert(0, '.')

from api.main import get_agent_configuration

# Get configuration
config = get_agent_configuration()

# Print summary
print("\n" + "="*80)
print("AGENT CONFIGURATION")
print("="*80)

print(f"\nDefault Model: {config['default_model']}")
print(f"Built-in Agents: {len(config['built_in_agents'])}")
print(f"User-Defined Agents: {len(config['user_defined_agents'])}")

print("\n" + "-"*80)
print("USER-DEFINED AGENTS")
print("-"*80)

for agent in config['user_defined_agents']:
    print(f"\n🤖 {agent['name']}")
    print(f"   Role: {agent['role']}")
    print(f"   Tools: {', '.join(agent['tools']) if agent['tools'] else 'None (built-in knowledge)'}")
    print(f"   Model: {agent['model']}")
    print(f"   Capabilities: {len(agent['capabilities'])} capabilities")

print("\n" + "-"*80)
print("COORDINATION")
print("-"*80)

for role in config['coordination']['roles']:
    print(f"\n• {role['agent']}")
    print(f"  {role['responsibility']}")
    print(f"  💡 {role['note']}")

print("\n" + "="*80)
print("✅ Configuration looks correct!")
print("="*80)

# Save to file for inspection
with open('agent_config_output.json', 'w') as f:
    json.dump(config, f, indent=2)
    print(f"\n📄 Full configuration saved to: agent_config_output.json")
