import asyncio
import logging
import sqlite3
import json
from tools.mcp_client import MCPClientManager
from memory.soul_db import SoulDB

async def list_claude_tools():
    logging.basicConfig(level=logging.INFO)
    db = SoulDB("nova26.db")
    manager = MCPClientManager(db)
    
    # Use the registered config for claude_code
    conn = sqlite3.connect("nova26.db")
    cursor = conn.cursor()
    cursor.execute("SELECT server_command, server_args_json, env_vars_json FROM mcp_tools WHERE tool_name = 'claude_code'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("claude_code not found in db")
        return
        
    cmd, args_json, env_json = row
    args = json.loads(args_json)
    env = json.loads(env_json)
    
    print(f"Connecting to {cmd}...")
    success = await manager.connect_tool("claude_code", cmd, args, env)
    
    if success:
        session = manager.active_sessions["claude_code"]
        tools = await session.list_tools()
        for tool in tools.tools:
            if tool.name == "Write":
                print(f"Write Schema: {json.dumps(tool.inputSchema, indent=2)}")
                break
    else:
        print("Failed to connect.")
    
    await manager.disconnect_tool("claude_code")

if __name__ == "__main__":
    asyncio.run(list_claude_tools())
