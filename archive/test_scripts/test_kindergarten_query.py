"""
Test the specific query that's failing: "Wo sind die Kindergärten in Karlsruhe"
"""
import logging
from api.team_config import TeamConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_kindergarten_query():
    """Test the kindergarten query"""
    topic = "Wo sind die Kindergärten in Karlsruhe"
    
    print("="*80)
    print("TESTING KINDERGARTEN QUERY")
    print("="*80)
    print(f"Topic: {topic}")
    print()
    
    try:
        # Create team
        print("Creating team...")
        team = TeamConfig.create_team(topic)
        print(f"✓ Team created: {team.id}")
        print()
        
        # Format prompt
        prompt = TeamConfig.format_research_prompt(topic)
        print("Running team...")
        print()
        
        # Run team
        response = team.run(prompt)
        print("✓ Team completed")
        print()
        
        # Check response
        print("Response details:")
        print(f"  Type: {type(response)}")
        print(f"  Has data: {hasattr(response, 'data')}")
        
        if hasattr(response, 'data'):
            print(f"  Data type: {type(response.data)}")
            if hasattr(response.data, '__dict__'):
                print(f"  Data attributes: {list(response.data.__dict__.keys())}")
                for key, value in response.data.__dict__.items():
                    if not key.startswith('_'):
                        print(f"    {key}: {type(value)} = {str(value)[:100] if value else 'None'}")
        
        print()
        print("="*80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print()
        print("="*80)
        print("TEST FAILED")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kindergarten_query()
