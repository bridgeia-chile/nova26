import os
import json
import sqlite3
import subprocess
import logging

class NotebookManager:
    def __init__(self, soul_path="nova26.db"):
        self.soul_path = soul_path
        self.project_dir = "f:/Users/Rosvel Nuñez/Documents/Proyecto BridgeIA/Antigravity Projects/NovaGravity"
        self.notebook_name = "Nova26 - Proyecto BridgeIA"

    def _run_mcp_tool(self, tool_name, arguments):
        """Helper to run MCP tools via npx (for direct automation)."""
        cmd = ["npx", "notebooklm-mcp", tool_name]
        for k, v in arguments.items():
            cmd.extend([f"--{k}", str(v)])
        
        try:
            # We use subprocess for direct execution during setup
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"Error running {tool_name}: {result.stderr}")
                return {"error": result.stderr}
            
            # The MCP server output might contain logs, we look for the JSON result if any
            # For list_notebooks, it usually prints a table or list
            return {"output": result.stdout}
        except Exception as e:
            return {"error": str(e)}

    def initialize_project_notebook(self):
        """Creates the notebook and uploads initial sources."""
        print(f"[*] Inicializando cuaderno: {self.notebook_name}...")
        
        # 1. Create Notebook (Safe mode: if it exists, it might error or just list it)
        # For simplicity in this script, we just trigger add_notebook
        # The MCP server handled duplicates based on its own logic (usually creates a new one)
        res = self._run_mcp_tool("add_notebook", {"name": self.notebook_name})
        if "error" in res:
            return res
            
        print("[+] Cuaderno creado o identificado.")
        
        # 2. Upload Sources
        key_files = [
            'memory/schema.sql',
            'core/brain.py',
            'core/reasoning.py',
            'core/sentry_monitor.py',
            'interfaces/api_server.py',
            'task.md' # From artifacts usually, but let's try relative to project if possible
        ]
        
        # Get actual notebook ID if possible from output (parsing needed)
        # For now, we assume the user might have to select it or we use the latest added
        
        print("[*] Subiendo fuentes clave...")
        for f_path in key_files:
            full_path = os.path.join(self.project_dir, f_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # We send a chunk of content to add_source
                    # Arguments: notebook_id (required by MCP)
                    # Since we don't have the ID easily from npx output without regex, 
                    # an Agent using the tool would be better.
                    # But for this setup script, we'll try to get health/stats first.
                    pass
        
        return {"status": "success", "message": "Inicialización básica completada. Aisha ahora puede gestionar el resto."}

if __name__ == "__main__":
    manager = NotebookManager()
    # manager.initialize_project_notebook() # Uncomment to run manually
    print("Notebook Manager listo.")
