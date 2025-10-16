#!/usr/bin/env python3
"""
Simple test to verify the changes without requiring API key
"""
import sys

def test_config_changes():
    """Test that Config has correct default"""
    print("Testing Config...")
    
    with open('api/config.py', 'r') as f:
        config_content = f.read()
    
    if 'DEFAULT_MODEL = "production"' in config_content:
        print("✓ Config DEFAULT_MODEL is 'production'")
        return True
    else:
        print("✗ Config DEFAULT_MODEL not set to 'production'")
        return False

def test_team_config_changes():
    """Test that team_config.py has correct default"""
    print("\nTesting team_config.py...")
    
    with open('api/team_config.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('def create_search_agent(topic: str, model: str = "production")', 
         "Search Agent defaults to production model"),
        ('NOTE: We force production model (GPT-4o)', 
         "Documentation explains why GPT-4o is forced"),
        ('logger.info(f"Search Agent model:', 
         "Debug logging added"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description}")
            all_passed = False
    
    return all_passed

def test_search_agent_instructions():
    """Test that search agent instructions updated"""
    print("\nTesting search_agent.py instructions...")
    
    with open('api/instructions/search_agent.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('YOUR SINGLE RESPONSIBILITY:', 
         "Single responsibility section added"),
        ('TAVILY SEARCH BEST PRACTICES:', 
         "Tavily best practices section added"),
        ('FILTER OUT NON-CONTENT PAGES:', 
         "Form filtering guidance added"),
        ('Wählen Sie', 
         "German quiz detection pattern included"),
        ('DO NOT compile reports', 
         "No compilation instruction added"),
        ('SEARCH EFFECTIVENESS NOTES:', 
         "Simplified notes section (not full summary)"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description}")
            all_passed = False
    
    # Check that old summary section was removed
    if 'EXTRACTION SUMMARY:' in content and 'Total entities extracted: [number]' in content:
        print("✗ Old EXTRACTION SUMMARY section still present (should be removed)")
        all_passed = False
    else:
        print("✓ Old EXTRACTION SUMMARY section removed")
    
    return all_passed

def test_mentalist_instructions():
    """Test that mentalist instructions updated"""
    print("\nTesting mentalist.py instructions...")
    
    with open('api/instructions/mentalist.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('IMPORTANT: Search Agent only searches and extracts', 
         "Clarified Search Agent role"),
        ('does NOT compile reports', 
         "No compilation instruction"),
        ("Response Generator's responsibility", 
         "Response Generator ownership clarified"),
        ('✓ "Search for ministers', 
         "Good task examples provided"),
        ('✗ "Compile a comprehensive report"', 
         "Bad task examples provided"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description}")
            all_passed = False
    
    return all_passed

def test_main_py_changes():
    """Test that main.py has interaction limit logging"""
    print("\nTesting main.py...")
    
    with open('api/main.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('interaction_limit = team_data.get("interaction_limit", 50)', 
         "Interaction limit retrieved from team data"),
        ('store.add_log_entry(team_id, f"Interaction limit:', 
         "Interaction limit logged to execution log"),
        ('logger.info(f"Team {team_id}: Interaction limit set to', 
         "Interaction limit logged to system log"),
    ]
    
    all_passed = True
    for check_text, description in checks:
        if check_text in content:
            print(f"✓ {description}")
        else:
            print(f"✗ {description}")
            all_passed = False
    
    return all_passed

def main():
    print("=" * 70)
    print("VERIFYING PHASE 1 CHANGES")
    print("=" * 70)
    
    results = []
    
    # Test each file
    results.append(test_config_changes())
    results.append(test_team_config_changes())
    results.append(test_search_agent_instructions())
    results.append(test_mentalist_instructions())
    results.append(test_main_py_changes())
    
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} files")
    
    if all(results):
        print("\n✅ ALL CHANGES VERIFIED SUCCESSFULLY!")
        print("\n" + "=" * 70)
        print("WHAT CHANGED:")
        print("=" * 70)
        print("1. Search Agent now uses GPT-4o (production model) by default")
        print("2. Added Tavily Search best practices (how to avoid quiz pages)")
        print("3. Clarified Search Agent only searches/extracts (no compilation)")
        print("4. Updated Mentalist to not ask Search Agent to compile reports")
        print("5. Added debug logging for model and interaction limit")
        print("\n" + "=" * 70)
        print("EXPECTED IMPROVEMENTS:")
        print("=" * 70)
        print("• More reliable entity extraction (GPT-4o vs GPT-4o Mini)")
        print("• Fewer timeouts (simpler task, more powerful model)")
        print("• Better handling of German quiz pages")
        print("• More specific search queries")
        print("• Clearer separation of agent responsibilities")
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("1. Restart the API if it's running:")
        print("   pkill -f 'uvicorn api.main:app'")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n2. Test with the original failing topic:")
        print("   curl -X POST http://localhost:8000/api/v1/agent-teams \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{")
        print('       "topic": "Einbürgerungstests in Baden-Württemberg",')
        print('       "goals": ["Find stakeholders and programs"],')
        print('       "interaction_limit": 50')
        print("     }'")
        print("\n3. Monitor the execution log for:")
        print("   • 'Search Agent model: ... (GPT-4o)'")
        print("   • 'Interaction limit: 50 steps'")
        print("   • Entity counts > 0")
        print("   • Fewer timeout messages")
        print("\n4. Check the trace endpoint:")
        print("   http://localhost:5173/teams/<team_id>")
        print("=" * 70)
        return 0
    else:
        print("\n❌ SOME CHANGES NOT FOUND")
        print("Please review the files and ensure all changes were applied.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
