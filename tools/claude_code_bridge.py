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

    async def delegate_task(self, prompt: str, workdir: str = ".", model: str = None) -> dict:
        """Sends a task to the Marcos sub-agent via standard Claude CLI."""
        import subprocess
        import os
        
        # Prepare environment
        env = os.environ.copy()
        env["ANTHROPIC_BASE_URL"] = "http://localhost:11434/v1"
        env["ANTHROPIC_API_KEY"] = "ollama"
        if model:
            env["CLAUDE_CODE_MODEL"] = model

        # Command to run (Non-interactive mode if possible, but Claude Code might need flags)
        # Using the PowerShell script as a wrapper is a good idea.
        script_path = os.path.join(os.getcwd(), "run-claude-ollama.ps1")
        
        # We'll execute it with the prompt as an argument or passed via stdin
        # For now, we'll try running it directly.
        try:
            cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path, prompt]
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            stdout, stderr = process.communicate(timeout=300) # 5 min timeout
            
            return {
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "result": stdout if process.returncode == 0 else f"Error: {stderr}"
            }
        except Exception as e:
            return {"error": f"Failed to execute Claude Code: {str(e)}"}
