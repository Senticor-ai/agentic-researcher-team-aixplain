#!/usr/bin/env python3
"""
Simple script to view database contents
Usage: python scripts/view_database.py
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("./data/teams.db")

def format_datetime(dt_str):
    """Format ISO datetime string"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str

def main():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Start the backend first to create the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM teams")
    total = cursor.fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"Honeycomb OSINT Agent Teams Database")
    print(f"{'='*80}\n")
    print(f"Database: {DB_PATH}")
    print(f"Total Teams: {total}\n")
    
    if total == 0:
        print("No teams found. Create a team through the UI to see data here.")
        conn.close()
        return
    
    # Get status distribution
    cursor.execute("SELECT status, COUNT(*) FROM teams GROUP BY status")
    print("Status Distribution:")
    for status, count in cursor.fetchall():
        print(f"  {status:12} {count:3} teams")
    print()
    
    # Get all teams
    cursor.execute("""
        SELECT team_id, topic, status, created_at, updated_at 
        FROM teams 
        ORDER BY created_at DESC
    """)
    
    print(f"{'='*80}")
    print("Recent Teams:")
    print(f"{'='*80}\n")
    
    for row in cursor.fetchall():
        team_id, topic, status, created_at, updated_at = row
        
        # Status emoji
        status_emoji = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }.get(status, '❓')
        
        print(f"{status_emoji} {status.upper():10} | {team_id}")
        print(f"   Topic: {topic}")
        print(f"   Created: {format_datetime(created_at)}")
        print(f"   Updated: {format_datetime(updated_at)}")
        print()
    
    conn.close()
    
    print(f"{'='*80}")
    print("\nCommands:")
    print("  View specific team: sqlite3 data/teams.db \"SELECT * FROM teams WHERE team_id='<id>'\"")
    print("  Delete team:        sqlite3 data/teams.db \"DELETE FROM teams WHERE team_id='<id>'\"")
    print("  Reset database:     rm data/teams.db && python -m api.main")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
