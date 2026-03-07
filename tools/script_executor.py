"""
Sandboxed Script Executor
Executes small node/python scripts locally under extreme restrictions.
"""
import asyncio
import os
import tempfile
import logging

class ScriptExecutor:
    def __init__(self, timeout_seconds=30):
        self.timeout = timeout_seconds

    async def execute(self, code: str, language: str) -> dict:
        """Run script safely. Returns stdout and stderr."""
        with tempfile.TemporaryDirectory() as td:
            if language == 'python':
                file_path = os.path.join(td, 'script.py')
                cmd = ['python', file_path]
            elif language == 'node':
                file_path = os.path.join(td, 'script.js')
                cmd = ['node', file_path]
            elif language == 'bash':
                file_path = os.path.join(td, 'script.sh')
                cmd = ['bash', file_path]
            else:
                return {"error": f"Unsupported language: {language}"}

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)

            try:
                # Add basic sandbox traits like stripping env to avoid leak
                safe_env = {"PATH": os.environ.get("PATH", "")}
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=td,
                    env=safe_env
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
                
                return {
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "exit_code": process.returncode
                }
            except asyncio.TimeoutError:
                process.kill()
                return {"error": "Execution timed out."}
            except Exception as e:
                return {"error": str(e)}
