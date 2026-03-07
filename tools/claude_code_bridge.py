"""
Claude Code Bridge
Sub-agent delegation for coding tasks.
"""
import json
import logging

class ClaudeCodeBridge:
    def __init__(self, tool_registry, mcp_client):
        self.registry = tool_registry
        self.mcp = mcp_client
        self.tool_name = "claude_code"

    async def delegate_task(self, prompt: str, workdir: str) -> dict:
        """Sends a task to the sub-agent via standard MCP tools interface."""
        schema = await self.registry.get_tool_schema(self.tool_name)
        if not schema:
            return {"error": "Claude Code MCP server is not registered or active."}
            
        import os
        # For proof of concept, we use the 'Write' tool directly.
        abs_path = os.path.abspath("hello_world.py")
        params = {
            "file_path": abs_path,
            "content": "print('Hello from Claude Code via Nova Gravity!')\n"
        }
        
        logging.info(f"Executing Write on {self.tool_name} with params {params}")
        result = await self.mcp.execute_tool(self.tool_name, "Write", params)
        return result
