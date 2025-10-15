#!/usr/bin/env python3
"""
Script to automatically add pytest markers to test files based on their characteristics
"""
import os
import re
from pathlib import Path

def analyze_test_file(filepath):
    """Analyze a test file to determine appropriate markers"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    markers = []
    
    # Check for existing markers
    has_markers = bool(re.search(r'@pytest\.mark\.', content))
    
    # Determine test type based on filename and content
    filename = os.path.basename(filepath)
    
    # E2E tests
    if 'e2e' in filename.lower() or 'end_to_end' in filename.lower():
        markers.append('e2e')
    
    # Integration tests
    elif any(keyword in filename.lower() for keyword in ['integration', 'api_integration']):
        markers.append('integration')
    
    # Check content for integration indicators
    elif any(keyword in content for keyword in [
        'curl', 'requests.', 'http://', 'localhost:',
        'TeamConfig.create_team', 'aixplain', 'ToolFactory'
    ]):
        if 'mock' not in content.lower() and 'Mock' not in content:
            markers.append('integration')
        else:
            markers.append('unit')
    
    # Default to unit test
    else:
        markers.append('unit')
    
    # Check for slow tests
    if 'sleep' in content or 'time.sleep' in content:
        markers.append('slow')
    
    # Check for regression tests
    if 'regression' in filename.lower() or 'TestEnhanced' in content:
        markers.append('regression')
    
    return markers, has_markers

def add_markers_to_file(filepath, markers):
    """Add markers to test functions in a file"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a test function or class definition
        if re.match(r'^(class Test|def test_)', line.strip()):
            # Check if markers already exist above this line
            has_marker = False
            if i > 0:
                prev_line = lines[i-1].strip()
                if prev_line.startswith('@pytest.mark.'):
                    has_marker = True
            
            # Add markers if they don't exist
            if not has_marker and markers:
                indent = len(line) - len(line.lstrip())
                for marker in markers:
                    new_lines.append(' ' * indent + f'@pytest.mark.{marker}\n')
                modified = True
        
        new_lines.append(line)
        i += 1
    
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    """Main function to process all test files"""
    tests_dir = Path('tests')
    test_files = list(tests_dir.glob('test_*.py'))
    
    print(f"Found {len(test_files)} test files")
    print()
    
    stats = {
        'unit': 0,
        'integration': 0,
        'e2e': 0,
        'regression': 0,
        'slow': 0,
        'modified': 0,
        'skipped': 0
    }
    
    for filepath in sorted(test_files):
        markers, has_markers = analyze_test_file(filepath)
        
        print(f"{filepath.name:50} -> {', '.join(markers)}")
        
        for marker in markers:
            if marker in stats:
                stats[marker] += 1
        
        if has_markers:
            stats['skipped'] += 1
        else:
            # Uncomment to actually modify files
            # if add_markers_to_file(filepath, markers):
            #     stats['modified'] += 1
            pass
    
    print()
    print("Summary:")
    print(f"  Unit tests: {stats['unit']}")
    print(f"  Integration tests: {stats['integration']}")
    print(f"  E2E tests: {stats['e2e']}")
    print(f"  Regression tests: {stats['regression']}")
    print(f"  Slow tests: {stats['slow']}")
    print(f"  Already have markers: {stats['skipped']}")
    print()
    print("To actually add markers, uncomment the modification code in the script")

if __name__ == '__main__':
    main()
