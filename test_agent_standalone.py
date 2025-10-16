#!/usr/bin/env env python3
"""
Standalone Agent Test Script

Test the Search Agent directly without the team overhead.
Useful for debugging tool configuration and agent behavior.
"""
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure aixplain SDK
if os.getenv("AIXPLAIN_API_KEY") and not os.getenv("TEAM_API_KEY"):
    os.environ["TEAM_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")

from api.config import Config
from api.team_config import TeamConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_search_agent(topic: str, verbose: bool = False):
    """
    Test the Search Agent standalone
    
    Args:
        topic: Research topic to test
        verbose: Show detailed output
    """
    print("=" * 80)
    print("STANDALONE AGENT TEST")
    print("=" * 80)
    print(f"\nTopic: {topic}")
    print(f"Model: {Config.get_model_name(Config.TEAM_AGENT_MODEL)}")
    print(f"Tavily Tool ID: {Config.TOOL_IDS.get('tavily_search', 'NOT CONFIGURED')}")
    print()
    
    try:
        # Create the Search Agent
        print("Creating Search Agent...")
        search_agent = TeamConfig.create_search_agent(topic)
        print(f"✓ Search Agent created: {search_agent.name}")
        print(f"  Agent ID: {search_agent.id}")
        print(f"  Tools: {[tool.name for tool in search_agent.tools] if hasattr(search_agent, 'tools') else 'N/A'}")
        print()
        
        # Create a simple research prompt
        prompt = f"""Research the following topic and extract key entities:

Topic: {topic}

Please provide:
1. Person entities with their roles and descriptions
2. Organization entities with their descriptions
3. Events with their descriptions and timeframes
4. Include source URLs for verification

Focus on finding accurate, verifiable information."""
        
        print("Running agent with prompt...")
        print("-" * 80)
        if verbose:
            print(f"Prompt:\n{prompt}")
            print("-" * 80)
        
        # Run the agent
        response = search_agent.run(prompt)
        
        print("\n" + "=" * 80)
        print("AGENT RESPONSE")
        print("=" * 80)
        
        # Parse response
        if hasattr(response, 'data'):
            data = response.data
            
            # Show output
            if hasattr(data, 'output'):
                print("\nOutput:")
                print("-" * 80)
                print(data.output)
                print("-" * 80)
            
            # Show execution stats
            if hasattr(data, 'executionStats'):
                stats = data.executionStats
                print("\nExecution Stats:")
                if hasattr(stats, '__dict__'):
                    for key, value in stats.__dict__.items():
                        if not key.startswith('_'):
                            print(f"  {key}: {value}")
                else:
                    print(f"  {stats}")
            
            # Show intermediate steps
            if hasattr(data, 'intermediate_steps') and data.intermediate_steps:
                print(f"\nIntermediate Steps: {len(data.intermediate_steps)}")
                if verbose:
                    for idx, step in enumerate(data.intermediate_steps, 1):
                        print(f"\n  Step {idx}:")
                        print(f"    {step}")
            
            # Check for errors
            if hasattr(data, 'output') and data.output:
                output_str = str(data.output).lower()
                if 'error' in output_str:
                    print("\n⚠️  WARNING: Error detected in output")
                    print("This might indicate:")
                    print("  - Tavily API key is invalid or expired")
                    print("  - Tool is not properly configured")
                    print("  - Agent lacks permissions")
                    print("  - Platform-level issues")
        else:
            print(f"Response: {response}")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)
        
        # Save full response to file
        output_file = f"test_agent_output_{topic.replace(' ', '_')}.json"
        try:
            response_dict = {}
            if hasattr(response, '__dict__'):
                for key, value in response.__dict__.items():
                    if not key.startswith('_') and not callable(value):
                        try:
                            if hasattr(value, '__dict__'):
                                response_dict[key] = {k: str(v) for k, v in value.__dict__.items() if not k.startswith('_')}
                            else:
                                response_dict[key] = str(value)
                        except:
                            response_dict[key] = str(value)
            
            with open(output_file, 'w') as f:
                json.dump(response_dict, f, indent=2)
            print(f"\n✓ Full response saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save response to file: {e}")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"\n{type(e).__name__}: {e}")
        
        import traceback
        if verbose:
            print("\nFull traceback:")
            print(traceback.format_exc())
        
        print("\nPossible causes:")
        print("  1. AIXPLAIN_API_KEY not set or invalid")
        print("  2. TAVILY_API_KEY not set or invalid")
        print("  3. Tool IDs not configured correctly")
        print("  4. Model ID not accessible")
        print("  5. Network connectivity issues")
        
        print("\nCheck your .env file:")
        print("  AIXPLAIN_API_KEY=your_key_here")
        print("  TAVILY_API_KEY=your_key_here")
        
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Search Agent standalone without team overhead"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default="Angela Merkel",
        help="Research topic to test (default: Angela Merkel)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output including prompts and traces"
    )
    
    args = parser.parse_args()
    
    # Run test
    success = test_search_agent(args.topic, args.verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
