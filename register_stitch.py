import sqlite3
import json

def register_stitch_tools():
    conn = sqlite3.connect('nova26.db')
    cursor = conn.cursor()
    
    tools = [
        {
            "name": "mcp_StitchMCP_create_project",
            "description": "Creates a new Stitch project.",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Optional title for the project"}
                }
            }
        },
        {
            "name": "mcp_StitchMCP_generate_screen_from_text",
            "description": "Generates a new screen within a project from a text prompt.",
            "schema": {
                "type": "object",
                "properties": {
                    "projectId": {"type": "string", "description": "Project ID"},
                    "prompt": {"type": "string", "description": "Text prompt to generate the screen"},
                    "deviceType": {"type": "string", "enum": ["MOBILE", "DESKTOP", "TABLET", "AGNOSTIC"]}
                },
                "required": ["projectId", "prompt"]
            }
        },
        {
            "name": "mcp_StitchMCP_edit_screens",
            "description": "Edits existing screens within a project using a text prompt.",
            "schema": {
                "type": "object",
                "properties": {
                    "projectId": {"type": "string", "description": "Project ID"},
                    "selectedScreenIds": {"type": "array", "items": {"type": "string"}},
                    "prompt": {"type": "string", "description": "Input text to edit the screens"},
                    "deviceType": {"type": "string", "enum": ["MOBILE", "DESKTOP", "TABLET", "AGNOSTIC"]}
                },
                "required": ["projectId", "selectedScreenIds", "prompt"]
            }
        },
        {
            "name": "mcp_StitchMCP_list_projects",
            "description": "Lists all Stitch projects accessible to the user.",
            "schema": {
                "type": "object",
                "properties": {
                    "filter": {"type": "string", "description": "view=owned or view=shared"}
                }
            }
        },
        {
            "name": "mcp_StitchMCP_list_screens",
            "description": "Lists all screens within a given Stitch project.",
            "schema": {
                "type": "object",
                "properties": {
                    "projectId": {"type": "string", "description": "Project ID"}
                },
                "required": ["projectId"]
            }
        }
    ]
    
    for t in tools:
        cursor.execute("DELETE FROM mcp_tools WHERE tool_name = ?", (t['name'],))
        cursor.execute(
            "INSERT INTO mcp_tools (tool_name, schema_json, server_command, is_active) VALUES (?, ?, ?, 1)",
            (t['name'], json.dumps({"name": t['name'], "description": t['description'], "input_schema": t['schema']}), "builtin_bridge")
        )
        
    conn.commit()
    conn.close()
    print("Stitch tools registered successfully.")

if __name__ == "__main__":
    register_stitch_tools()
