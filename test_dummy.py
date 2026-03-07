import asyncio
import logging
from tools.mcp_client import MCPClientManager

from memory.soul_db import SoulDB

async def test_dummy():
    logging.basicConfig(level=logging.INFO)
    db = SoulDB("nova26.db")
    manager = MCPClientManager(db)
    
    print("Connecting to dummy_tool...")
    success = await manager.connect_tool(
        "dummy_tool", 
        "python", 
        ["tools/dummy_mcp.py"], 
        {}
    )
    
    if success:
        print("Connection successful!")
        await manager.disconnect_tool("dummy_tool")
    else:
        print("Connection failed.")

if __name__ == "__main__":
    asyncio.run(test_dummy())
