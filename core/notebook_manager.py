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

    async def initialize_project_notebook(self, mcp_manager):
        """Creates the notebook and uploads initial sources using MCP."""
        print(f"[*] Inicializando cuaderno: {self.notebook_name}...")
        
        # 1. Connect to NotebookLM MCP
        # command, args, env should be fetched from DB normally, but for npx we can use defaults
        success = await mcp_manager.connect_tool(
            "notebooklm", 
            "npx.cmd", 
            ["notebooklm-mcp", "run"], 
            {}
        )
        
        if not success:
            return {"error": "No se pudo conectar al servidor MCP de NotebookLM."}

        # 2. Check if notebook exists
        try:
            res = await mcp_manager.execute_tool("notebooklm", "list_notebooks", {})
            notebooks_raw = res.get("result", "[]")
            # The result might be a string representation of a list or a table
            # For simplicity, we create it and rely on the server handling duplicates
            
            print("[*] Creando cuaderno...")
            create_res = await mcp_manager.execute_tool(
                "notebooklm", 
                "add_notebook", 
                {"name": self.notebook_name}
            )
            
            # Since IDs are hard to predict from just text, we assume Aisha will handle
            # the finer details. This script sets the stage.
            
            return {"status": "success", "message": "Canal de NotebookLM abierto y cuaderno solicitado."}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    manager = NotebookManager()
    # manager.initialize_project_notebook() # Uncomment to run manually
    print("Notebook Manager listo.")
