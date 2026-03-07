import os
from pathlib import Path

class FileEditor:
    """Basic tool for reading and writing files autonomously."""
    
    def execute(self, operation: str, filename: str, content: str = None) -> str:
        path = Path(filename)
        
        if operation == "read":
            if not path.exists():
                return f"ERROR: Archivo {filename} no existe."
            return path.read_text(encoding='utf-8')
            
        elif operation == "write":
            path.write_text(content, encoding='utf-8')
            return f"SUCCESS: Archivo {filename} escrito correctamente."
            
        elif operation == "append":
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"SUCCESS: Contenido añadido a {filename}."
            
        return f"ERROR: Operación {operation} no reconocida."
