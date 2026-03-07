import sqlite3
import json

def check_db():
    conn = sqlite3.connect('nova26.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t['name'] for t in tables])
    
    if 'mcp_tools' in [t['name'] for t in tables]:
        cursor.execute("SELECT * FROM mcp_tools")
        rows = cursor.fetchall()
        print("\nMCP Tools:")
        for row in rows:
            print(dict(row))
    else:
        print("\nTable 'mcp_tools' not found.")
    
    conn.close()

if __name__ == "__main__":
    check_db()
