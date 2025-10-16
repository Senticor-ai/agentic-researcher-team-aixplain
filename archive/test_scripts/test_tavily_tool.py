#!/usr/bin/env python3
"""
Test Tavily Tool Access

Simple script to verify Tavily tool is accessible and working.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure aixplain SDK
if os.getenv("AIXPLAIN_API_KEY") and not os.getenv("TEAM_API_KEY"):
    os.environ["TEAM_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")

print("=" * 80)
print("TAVILY TOOL ACCESS TEST")
print("=" * 80)

# Check environment variables
print("\n1. Checking Environment Variables...")
print("-" * 80)

aixplain_key = os.getenv("AIXPLAIN_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if aixplain_key:
    print(f"✓ AIXPLAIN_API_KEY: {aixplain_key[:10]}...{aixplain_key[-4:]}")
else:
    print("✗ AIXPLAIN_API_KEY: NOT SET")

if tavily_key:
    print(f"✓ TAVILY_API_KEY: {tavily_key[:10]}...{tavily_key[-4:]}")
else:
    print("✗ TAVILY_API_KEY: NOT SET")

# Check config
print("\n2. Checking Configuration...")
print("-" * 80)

try:
    from api.config import Config
    
    print(f"Model ID: {Config.TEAM_AGENT_MODEL}")
    print(f"Model Name: {Config.get_model_name(Config.TEAM_AGENT_MODEL)}")
    
    if 'tavily_search' in Config.TOOL_IDS:
        print(f"✓ Tavily Tool ID: {Config.TOOL_IDS['tavily_search']}")
    else:
        print("✗ Tavily Tool ID: NOT CONFIGURED")
        
except Exception as e:
    print(f"✗ Error loading config: {e}")

# Try to access the tool
print("\n3. Testing Tool Access...")
print("-" * 80)

try:
    from aixplain.factories import ToolFactory
    from api.config import Config
    
    if 'tavily_search' not in Config.TOOL_IDS:
        print("✗ Cannot test - Tavily tool ID not configured")
        sys.exit(1)
    
    tool_id = Config.TOOL_IDS['tavily_search']
    print(f"Fetching tool: {tool_id}")
    
    tool = ToolFactory.get(tool_id)
    print(f"✓ Tool fetched successfully")
    print(f"  Name: {tool.name}")
    print(f"  ID: {tool.id}")
    
    if hasattr(tool, 'description'):
        print(f"  Description: {tool.description}")
    
    # Try to run a simple search
    print("\n4. Testing Tool Execution...")
    print("-" * 80)
    print("Running test search: 'Python programming'")
    
    result = tool.run("Python programming")
    
    print("✓ Tool executed successfully")
    print(f"Result type: {type(result)}")
    
    if hasattr(result, 'data'):
        print(f"Has data: Yes")
        if hasattr(result.data, 'output'):
            output = str(result.data.output)
            print(f"Output length: {len(output)} characters")
            print(f"Output preview: {output[:200]}...")
    else:
        print(f"Result: {str(result)[:200]}...")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print("\nThe Tavily tool is accessible and working correctly.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    
    print("\n" + "=" * 80)
    print("✗ TEST FAILED")
    print("=" * 80)
    
    print("\nPossible issues:")
    print("  1. Tavily API key is invalid or expired")
    print("  2. Tool ID is incorrect")
    print("  3. aixplain API key lacks permissions")
    print("  4. Network connectivity issues")
    print("  5. Tavily service is down")
    
    print("\nTo fix:")
    print("  1. Check your .env file has valid keys")
    print("  2. Verify tool ID in api/config.py")
    print("  3. Test Tavily API directly: https://tavily.com")
    
    sys.exit(1)
