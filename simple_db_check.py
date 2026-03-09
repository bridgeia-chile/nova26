import sqlite3
import os

db_path = "nova26.db"

if os.path.exists(db_path):
    print(f"Checking DB: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    for table in ['agents', 'models', 'llm_providers', 'mcp_tools', 'episodic']:
        if table in tables:
            print(f"\n--- {table} ---")
            if table == 'episodic':
                cursor.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 10;")
            else:
                cursor.execute(f"SELECT * FROM {table};")
            for row in cursor.fetchall():
                print(dict(row))
            
    conn.close()
else:
    print(f"DB not found at {db_path}")
