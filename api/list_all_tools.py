"""
Script to list all available tools from aixplain marketplace
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables BEFORE importing aixplain
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

from aixplain.factories import ToolFactory

print("Listing all available tools from aixplain marketplace...")
print("=" * 80)

try:
    # List all tools with pagination
    page = 0
    page_size = 50
    all_tools = []
    
    while True:
        print(f"\nFetching page {page}...")
        tools_response = ToolFactory.list(page_number=page, page_size=page_size)
        
        if not tools_response or 'results' not in tools_response:
            break
            
        results = tools_response.get('results', [])
        if not results:
            break
            
        all_tools.extend(results)
        page += 1
        
        # Stop if we got fewer results than page size (last page)
        if len(results) < page_size:
            break
    
    print(f"\n{'='*80}")
    print(f"Found {len(all_tools)} tools total")
    print(f"{'='*80}\n")
    
    # Print all tools
    for i, tool in enumerate(all_tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   ID: {tool.id}")
        if hasattr(tool, 'description') and tool.description:
            desc = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
            print(f"   Description: {desc}")
        print()
    
    # Highlight search-related tools
    print(f"\n{'='*80}")
    print("SEARCH-RELATED TOOLS:")
    print(f"{'='*80}\n")
    
    search_tools = [t for t in all_tools if any(keyword in t.name.lower() 
                    for keyword in ['search', 'google', 'serper', 'tavily', 'web'])]
    
    if search_tools:
        for tool in search_tools:
            print(f"✓ {tool.name} - ID: {tool.id}")
            if hasattr(tool, 'description') and tool.description:
                print(f"  {tool.description[:150]}")
            print()
    else:
        print("No search-related tools found")

except Exception as e:
    print(f"Error listing tools: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
