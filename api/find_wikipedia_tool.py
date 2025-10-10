"""
Script to find Wikipedia tool in aixplain
"""
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from aixplain.factories import ToolFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to get Wikipedia tool by searching
try:
    # Common Wikipedia tool IDs from aixplain documentation
    potential_ids = [
        "wikipedia",
        "wikipedia_search",
        "wiki",
    ]
    
    print("Searching for Wikipedia tool...")
    
    # Try to list all available tools
    try:
        tools = ToolFactory.list()
        print(f"\nFound {len(tools.get('results', []))} tools")
        
        # Search for Wikipedia-related tools
        for tool in tools.get('results', []):
            if 'wiki' in tool.name.lower() or 'wikipedia' in tool.name.lower():
                print(f"  Found: {tool.name} - ID: {tool.id}")
    except Exception as e:
        print(f"Could not list tools: {e}")
    
    # Try common Wikipedia tool ID from aixplain marketplace
    # Based on aixplain documentation, Wikipedia tool is typically available
    print("\nTrying to get Wikipedia tool directly...")
    
    # Try the Wikipedia API tool (common ID)
    try:
        wiki_tool = ToolFactory.get("wikipedia")
        print(f"Success! Wikipedia tool: {wiki_tool.name} - ID: {wiki_tool.id}")
    except Exception as e:
        print(f"Could not get 'wikipedia' tool: {e}")
    
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
