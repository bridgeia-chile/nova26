import sqlite3
import os

def verify_db():
    db_path = 'nova26.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tool_name, server_command, server_args_json, env_vars_json FROM mcp_tools WHERE tool_name='claude_code'")
    row = cursor.fetchone()
    if row:
        print(f"Tool: {row[0]}")
        print(f"Command: {row[1]}")
        print(f"Args: {row[2]}")
        print(f"Env: {row[3]}")
    else:
        print("Tool 'claude_code' not found in mcp_tools")
    conn.close()

if __name__ == "__main__":
    verify_db()
