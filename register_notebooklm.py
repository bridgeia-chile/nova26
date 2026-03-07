import sqlite3
import json

def register_notebooklm():
    conn = sqlite3.connect('nova26.db')
    cursor = conn.cursor()
    
    server_cmd = "npx notebooklm-mcp run"
    
    tools = [
        {
            "name": "mcp_notebooklm_list_notebooks",
            "description": "List all notebooks in your library.",
            "schema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "mcp_notebooklm_add_notebook",
            "description": "Create a new notebook.",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the notebook"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "mcp_notebooklm_add_source",
            "description": "Add a source to a notebook.",
            "schema": {
                "type": "object",
                "properties": {
                    "notebook_id": {"type": "string", "description": "The ID of the notebook"},
                    "source_name": {"type": "string", "description": "Name for the source"},
                    "content": {"type": "string", "description": "Text content of the source"}
                },
                "required": ["notebook_id", "source_name", "content"]
            }
        },
        {
            "name": "mcp_notebooklm_ask_question",
            "description": "Ask a question within a notebook context.",
            "schema": {
                "type": "object",
                "properties": {
                    "notebook_id": {"type": "string", "description": "The ID of the notebook"},
                    "question": {"type": "string", "description": "The question to ask"}
                },
                "required": ["notebook_id", "question"]
            }
        }
    ]
    
    for t in tools:
        cursor.execute("DELETE FROM mcp_tools WHERE tool_name = ?", (t['name'],))
        cursor.execute(
            "INSERT INTO mcp_tools (tool_name, schema_json, server_command, is_active) VALUES (?, ?, ?, 1)",
            (t['name'], json.dumps({"name": t['name'], "description": t['description'], "input_schema": t['schema']}), server_cmd)
        )
    
    conn.commit()
    conn.close()
    print("NotebookLM tools registered successfully.")

if __name__ == "__main__":
    register_notebooklm()
