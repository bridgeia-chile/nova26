import asyncio
import os
from core.brain import NovaGravityBrain
from dotenv import load_dotenv
from pathlib import Path

async def verify():
    load_dotenv()
    print("[*] Iniciando verificación de Fase 3...")
    
    # Asegurarse de que el archivo no exista
    target_file = Path("chile_info.txt")
    if target_file.exists():
        target_file.unlink()
        
    brain = NovaGravityBrain("nova26.db")
    await brain.boot()
    
    prompt = (
        "Busca en la web usando la herramienta 'web_search' (método search) "
        "cuál es la capital de Chile. Luego, crea un archivo llamado 'chile_info.txt' "
        "usando 'os_navigation' (método write) que contenga la respuesta. "
        "Finalmente, confírmame que lo has hecho."
    )
    
    print(f"[*] Enviando prompt: {prompt}")
    response = await brain.process_input(prompt, interface='verify_script')
    
    print("\n" + "="*50)
    print("RESPUESTA DE NOVA26:")
    print(response)
    print("="*50 + "\n")
    
    if target_file.exists():
        content = target_file.read_text(encoding='utf-8')
        print(f"[OK] Archivo 'chile_info.txt' creado con éxito.")
        print(f"Contenido: {content}")
    else:
        print("[ERROR] El archivo 'chile_info.txt' no fue creado.")

if __name__ == "__main__":
    asyncio.run(verify())
