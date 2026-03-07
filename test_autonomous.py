import asyncio
import os
from pathlib import Path
from core.brain import NovaGravityBrain
from dotenv import load_dotenv

async def run_test():
    load_dotenv()
    # 1. Setup environment
    if not os.path.exists("skills"):
        os.makedirs("skills")
        
    # 2. Boot Nova
    brain = NovaGravityBrain("nova26.db")
    await brain.boot()
    
    # 3. Create a BROKEN script to fix
    broken_file = Path("broken_test.py")
    broken_file.write_text("print('Hello world' -- syntax error here")
    
    # 4. Prompt Nova to fix it
    prompt = "Hay un error de sintaxis en 'broken_test.py'. Léelo usando FileEditor, corrígelo y ejecútalo con ScriptExecutor hasta que funcione."
    
    response = await brain.process_input(prompt, interface='test')
    
    # 5. Verify fix (using safe prints for Windows)
    if "SUCCESS" in response or "Hello world" in response:
        print("\n[OK] TEST EXITOSO: Nova corrigio el script.")
    else:
        print(f"\n[FAIL] TEST FALLIDO: Nova no logro corregir el script: {response[:100]}")

if __name__ == "__main__":
    asyncio.run(run_test())
