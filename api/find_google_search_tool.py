"""
Script to find Google Search tool ID from aixplain marketplace
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import from api module
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables from root directory BEFORE importing aixplain
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

# Now import aixplain after environment is set
from aixplain.factories import ToolFactory

print("Searching for Google Search tool in aixplain marketplace...")
print("=" * 60)

# Try to search for Google Search tool
try:
    # Try common Google Search tool names and alternatives
    potential_names = [
        "google_search",
        "google-search",
        "Google Search",
        "GoogleSearch",
        "google",
        "serper",
        "Serper",
        "serper_search",
        "google_serper",
    ]
    
    print("\nTrying to get Google Search tool directly...")
    
    # Try each potential name
    for name in potential_names:
        try:
            tool = ToolFactory.get(name)
            print(f"✓ Success! Found tool: {tool.name} - ID: {tool.id}")
            print(f"  Description: {tool.description if hasattr(tool, 'description') else 'N/A'}")
            break
        except Exception as e:
            print(f"✗ Could not get '{name}' tool: {e}")
    
    # Try listing all tools to find Google Search or Serper
    print("\nSearching all available tools for 'google' or 'serper'...")
    try:
        # Note: This may not work depending on aixplain API permissions
        tools = ToolFactory.list()
        found = False
        for tool in tools.get('results', []):
            tool_name_lower = tool.name.lower()
            if 'google' in tool_name_lower or 'serper' in tool_name_lower or 'search' in tool_name_lower:
                print(f"  ✓ Found: {tool.name} - ID: {tool.id}")
                if hasattr(tool, 'description'):
                    print(f"    Description: {tool.description}")
                found = True
        if not found:
            print("  No Google/Serper Search tools found in listing")
    except Exception as e:
        print(f"  Could not list tools: {e}")
        print("  Note: Tool listing may require special permissions")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("If you found the tool ID above, add it to api/config.py:")
print('TOOL_IDS = {')
print('    "tavily_search": "6736411cf127849667606689",')
print('    "wikipedia": "6633fd59821ee31dd914e232",')
print('    "google_search": "YOUR_GOOGLE_SEARCH_TOOL_ID_HERE",')
print('}')
