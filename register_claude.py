import sqlite3
import json
import os

def register_claude():
    db_path = 'nova26.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tool_name = "claude_code"
    # Testing direct execution bypassing the wrapper
    server_command = r"C:\Users\Rosvel Nuñez\.local\bin\claude.exe"
    server_args = ["mcp", "serve"]
    
    # Environment variables
    env_vars = {
        "ANTHROPIC_BASE_URL": "http://localhost:11434",
        "ANTHROPIC_API_KEY": "ollama",
        "ANTHROPIC_MODEL": "devstral-2:123b-cloud",
        "CI": "1",
        "FORCE_COLOR": "0"
    }
    
    # Generic schema for a coding agent task
    schema = {
        "name": "code_task",
        "description": "Delegates a coding or research task to Claude Code sub-agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The specific task description for Claude."},
                "workdir": {"type": "string", "description": "The working directory for the task."},
                "allowed_tools": {"type": "array", "items": {"type": "string"}, "description": "List of tools Claude can use (default: ['*'])"}
            },
            "required": ["prompt", "workdir"]
        }
    }
    
    cursor.execute("""
        INSERT OR REPLACE INTO mcp_tools 
        (tool_name, server_command, server_args_json, env_vars_json, schema_json, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        tool_name,
        server_command,
        json.dumps(server_args),
        json.dumps(env_vars),
        json.dumps(schema),
        1
    ))
    
    conn.commit()
    print(f"Tool '{tool_name}' registered successfully.")
    conn.close()

if __name__ == "__main__":
    register_claude()
