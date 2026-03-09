import json
import logging

class NotebookLMHelper:
    """Helper to bridge Nova26 memory and NotebookLM MCP tools."""
    
    def __init__(self, memory_manager):
        self.memory = memory_manager

    async def prepare_backup_text(self):
        """Extracts recent episodic and semantic memory to a Markdown format."""
        # Get recent episodes (last 50)
        episodes = await self.memory.get_recent_episodic(limit=50)
        
        # Get top semantic memories
        semantics = await self.memory.search_semantic()

        content = "# Nova26 Memory Backup\n\n"
        
        content += "## Episodic Memory (Recent Conversations)\n"
        for ep in episodes:
            role = ep.get('role', 'unknown')
            text = ep.get('content', '')
            ts = ep.get('timestamp', '')
            content += f"- **[{ts}] {role.upper()}:** {text}\n"

        content += "\n## Semantic Memory (Established Knowledge)\n"
        for sem in semantics:
            key = sem.get('key', '')
            val = sem.get('value', '')
            content += f"- **{key}:** {val}\n"

        return content

    async def backup_to_notebook(self, brain, notebook_id):
        """Orchestrates the backup using brain's tool execution logic."""
        backup_content = await self.prepare_backup_text()
        
        import datetime
        source_name = f"Nova26_Backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Call the MCP tool via brain._act
        # Tool: mcp_notebooklm_add_source
        tool_input = {
            "notebook_id": notebook_id,
            "source_name": source_name,
            "content": backup_content
        }
        
        decision = {
            "action_type": "use_tool",
            "required_tool": "mcp_notebooklm_add_source",
            "tool_input": tool_input
        }
        
        logging.info(f"Iniciando respaldo en NotebookLM: {source_name}")
        return await brain._act(decision)
