"""
MCP Client
Connects to external MCP tools/servers registered in the db.
"""
import logging
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientManager:
    def __init__(self, soul_db):
        self.db = soul_db
        self.active_sessions = {} # tool_name -> session

    async def connect_tool(self, tool_name: str, command: str, args: list, env: dict):
        """Establish stdio connection to an MCP server."""
        import os
        import shutil
        
        # Windows fix for npx/npm/node
        if os.name == 'nt':
            if command in ['npx', 'npm', 'node']:
                actual_cmd = shutil.which(command)
                if not actual_cmd and command in ['npx', 'npm']:
                    actual_cmd = shutil.which(f"{command}.cmd")
                
                if actual_cmd:
                    logging.info(f"Resolved {command} to {actual_cmd}")
                    command = actual_cmd
                else:
                    logging.warning(f"Could not resolve {command} in PATH for tool {tool_name}")

        logging.info(f"Attempting to connect to MCP tool: {tool_name} with command: {command} {' '.join(args)}")
        try:
            server_params = StdioServerParameters(command=command, args=args, env=env)
            
            # We use a persistent session management approach
            async def _persist_connection():
                logging.info(f"Starting background connection task for {tool_name}")
                try:
                    async with stdio_client(server_params) as (read, write):
                        logging.info(f"Stdio client established for {tool_name}")
                        async with ClientSession(read, write) as session:
                            logging.info(f"Client session created for {tool_name}, initializing...")
                            await session.initialize()
                            self.active_sessions[tool_name] = session
                            logging.info(f"Connected to MCP tool: {tool_name}")
                            
                            # Keep the connection alive until removed
                            while tool_name in self.active_sessions and self.active_sessions[tool_name] == session:
                                await asyncio.sleep(1)
                            logging.info(f"Connection for {tool_name} gracefully closing.")
                except Exception as e:
                    logging.error(f"MCP Session {tool_name} crashed: {str(e)}", exc_info=True)
                    if tool_name in self.active_sessions:
                        del self.active_sessions[tool_name]
            
            # Run the connection in the background
            asyncio.create_task(_persist_connection())
            
            # Wait for session to be ready (increased timeout)
            for i in range(30):
                if tool_name in self.active_sessions:
                    logging.info(f"Tool {tool_name} is ready after {i*0.5}s")
                    return True
                await asyncio.sleep(0.5)
            
            logging.warning(f"Timeout waiting for tool {tool_name} to connect.")
            return False
        except Exception as e:
            logging.error(f"Failed to initiate connection for MCP {tool_name}: {str(e)}", exc_info=True)
            return False

    async def execute_tool(self, tool_name: str, method: str, params: dict):
        """Execute a method on the connected tool."""
        session = self.active_sessions.get(tool_name)
        if not session:
            raise RuntimeError(f"Tool {tool_name} is not connected or session lost.")
            
        logging.info(f"Executing {method} on {tool_name} with params {params}")
        
        try:
            result = await session.call_tool(method, params)
            output = ""
            if hasattr(result, 'content'):
                for block in result.content:
                    if hasattr(block, 'text'):
                        output += block.text
                    else:
                        output += str(block)
            else:
                output = str(result)
            return {"result": output}
        except Exception as e:
            logging.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
            return {"error": str(e)}

    async def disconnect_tool(self, tool_name: str):
        if tool_name in self.active_sessions:
            del self.active_sessions[tool_name]
            logging.info(f"Disconnected MCP tool: {tool_name}")
