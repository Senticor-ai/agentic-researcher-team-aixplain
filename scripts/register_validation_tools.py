#!/usr/bin/env python3
"""
Register Validation Tools with aixplain

This script registers the schema.org validator and URL verifier tools
with aixplain so they can be used by the Validation Agent.

Run this script once to register the tools, then update api/config.py
with the returned tool IDs.

Usage:
    python scripts/register_validation_tools.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from aixplain.factories import ToolFactory
from aixplain.modules.model.utility_model import BaseUtilityModelParams
from api.schema_org_validator_tool import validate_schema_org_json
from api.url_verifier_tool import verify_urls_json

def register_schema_validator():
    """Register schema.org validator tool"""
    print("\n" + "="*80)
    print("Registering Schema.org Validator Tool")
    print("="*80)
    
    try:
        params = BaseUtilityModelParams(
            name="Schema.org Validator",
            description=(
                "Validates entities against schema.org specifications. "
                "Checks for valid @context, @type, and properties. "
                "Returns validation results with issues and suggested corrections. "
                "Input: JSON string of entity. Output: JSON string with validation results."
            ),
            code=validate_schema_org_json
        )
        
        tool = ToolFactory.create(params=params)
        
        print(f"\n✅ Schema.org Validator registered successfully!")
        print(f"   Tool ID: {tool.id}")
        print(f"   Tool Name: {tool.name}")
        
        return tool.id
        
    except Exception as e:
        print(f"\n❌ Failed to register Schema.org Validator: {e}")
        import traceback
        traceback.print_exc()
        return None


def register_url_verifier():
    """Register URL verifier tool"""
    print("\n" + "="*80)
    print("Registering URL Verifier Tool")
    print("="*80)
    
    try:
        params = BaseUtilityModelParams(
            name="URL Verifier",
            description=(
                "Verifies URLs are valid and accessible. "
                "Checks URL format and performs HTTP HEAD requests to verify accessibility. "
                "Returns verification results with status codes and issues. "
                "Input: JSON string array of URLs. Output: JSON string with verification results."
            ),
            code=verify_urls_json
        )
        
        tool = ToolFactory.create(params=params)
        
        print(f"\n✅ URL Verifier registered successfully!")
        print(f"   Tool ID: {tool.id}")
        print(f"   Tool Name: {tool.name}")
        
        return tool.id
        
    except Exception as e:
        print(f"\n❌ Failed to register URL Verifier: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main registration function"""
    print("\n" + "="*80)
    print("VALIDATION TOOLS REGISTRATION")
    print("="*80)
    print("\nThis script will register custom Python validation tools with aixplain.")
    print("The tools will be available for use by the Validation Agent.")
    
    # Check for API key
    if not os.getenv("TEAM_API_KEY"):
        print("\n❌ ERROR: TEAM_API_KEY not found in environment")
        print("   Please set your API key in .env file")
        return 1
    
    print("\n✓ API key found")
    
    # Register tools
    schema_validator_id = register_schema_validator()
    url_verifier_id = register_url_verifier()
    
    # Summary
    print("\n" + "="*80)
    print("REGISTRATION COMPLETE")
    print("="*80)
    
    if schema_validator_id and url_verifier_id:
        print("\n✅ Both tools registered successfully!")
        print("\n📝 Next steps:")
        print("   1. Update api/config.py with the following tool IDs:")
        print(f'\n      "schema_validator": "{schema_validator_id}",')
        print(f'      "url_verifier": "{url_verifier_id}",')
        print("\n   2. Run integration tests to verify Validation Agent works:")
        print("      pytest tests/test_agent_workflow_integration.py -v")
        return 0
    else:
        print("\n❌ Tool registration failed")
        print("   Check the error messages above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
