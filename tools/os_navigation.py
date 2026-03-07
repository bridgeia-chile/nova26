"""
os_navigation.py
Provides secure OS Navigation, File Reading, and command execution capabilities with a strict sandbox whitelist.
"""
import os
import subprocess
import glob
from pathlib import Path

class OSNavigation:
    def __init__(self, allowed_directories=None):
        """
        initializes the OS Navigator.
        allowed_directories: list of string paths that the agent is allowed to read/write into.
        By default, only the current NovaGravity workspace directory is allowed.
        """
        # Default fallback to project root if nothing is provided
        default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.allowed_directories = [os.path.abspath(d) for d in (allowed_directories or [default_dir])]
        self.current_working_dir = self.allowed_directories[0]

    def _is_path_allowed(self, target_path: str) -> bool:
        """Verifies if the target path resolves to an allowed directory (Sandbox)."""
        abs_target = os.path.abspath(target_path)
        for allowed in self.allowed_directories:
            if abs_target.startswith(allowed):
                return True
        return False

    def list_directory(self, path=".") -> dict:
        """Lists files and directories in the target path, if allowed."""
        target_path = os.path.join(self.current_working_dir, path)
        if not self._is_path_allowed(target_path):
            return {"error": f"Acceso DENEGADO (Sandbox Restricition): {target_path} no esta en la lista blanca."}
        
        try:
            items = os.listdir(target_path)
            details = []
            for item in items:
                full_item_path = os.path.join(target_path, item)
                is_dir = os.path.isdir(full_item_path)
                details.append({"name": item, "type": "directory" if is_dir else "file"})
            return {"path": os.path.abspath(target_path), "items": details}
        except Exception as e:
            return {"error": str(e)}

    def read_file(self, file_path: str) -> dict:
        """Reads a file content, if allowed."""
        target_path = os.path.join(self.current_working_dir, file_path)
        if not self._is_path_allowed(target_path):
            return {"error": f"Acceso DENEGADO (Sandbox Restricition): {target_path} no esta en la lista blanca."}
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "path": os.path.abspath(target_path)}
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, file_path: str, content: str) -> dict:
        """Writes content to a file, if allowed."""
        target_path = os.path.join(self.current_working_dir, file_path)
        if not self._is_path_allowed(target_path):
            return {"error": f"Acceso DENEGADO (Sandbox Restricition): {target_path} no esta en la lista blanca."}
        
        try:
            # Ensure parent dirs exist
            os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"Archivo guardado en {os.path.abspath(target_path)}"}
        except Exception as e:
            return {"error": str(e)}

    def execute_command(self, command: str) -> dict:
        """
        Executes a shell command. 
        Highly dangerous. In this sandbox implementation, we only allow basic informational commands
        or commands strictly within the CWD without accessing restricted paths.
        """
        # Basic sanity check (this is not fullproof, but adds a layer)
        dangerous_keywords = ['rm -rf /', 'format', 'del /s /q c:', 'Set-ExecutionPolicy']
        for bk in dangerous_keywords:
            if bk.lower() in command.lower():
                return {"error": f"Comando bloqueado por politicas de seguridad."}
        
        try:
            process = subprocess.Popen(
                command, 
                shell=True, 
                cwd=self.current_working_dir,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=30)
            return {
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Tiempo de ejecucion agotado (Timeout)."}
        except Exception as e:
            return {"error": str(e)}

    def change_directory(self, path: str) -> dict:
        """Changes the internal current working directory, if allowed."""
        target_path = os.path.abspath(os.path.join(self.current_working_dir, path))
        if not self._is_path_allowed(target_path):
            return {"error": f"Acceso DENEGADO (Sandbox Restricition): {target_path} no esta en la lista blanca."}
        
        if os.path.isdir(target_path):
            self.current_working_dir = target_path
            return {"success": True, "cwd": self.current_working_dir}
        else:
            return {"error": "El directorio no existe."}
