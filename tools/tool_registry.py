"""
Tool Registry
Registers and tracks available tools statically and actively via MCP.
"""
import json
import logging
import asyncio

class ToolRegistry:
    def __init__(self, soul_db, mcp_client):
        self.db = soul_db
        self.mcp_client = mcp_client
        self.registered_tools = {}

    async def load_from_db(self):
        """Loads all active tools from the database."""
        async with self.db.conn.execute("SELECT * FROM mcp_tools WHERE is_active = 1") as cursor:
            rows = await cursor.fetchall()
            
        for row in rows:
            tool = dict(row)
            name = tool['tool_name']
            command = tool['server_command']
            args = json.loads(tool['server_args_json'] or "[]")
            env = json.loads(tool['env_vars_json'] or "{}")
            
            self.registered_tools[name] = tool
            # Reconnect MCP clients seamlessly
            asyncio.create_task(self.mcp_client.connect_tool(name, command, args, env))
            
    async def get_tool_schema(self, tool_name: str):
        """Return the schema dictionary for the requested tool."""
        tool = self.registered_tools.get(tool_name)
        if not tool: return None
        return json.loads(tool.get('schema_json') or "{}")
