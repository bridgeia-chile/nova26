import asyncio
import os
from dotenv import load_dotenv
from core.brain import NovaGravityBrain

load_dotenv()

async def run_test():
    print("Iniciando nova26 Brain...")
    brain = NovaGravityBrain(os.getenv('SOUL_DB_PATH', "nova26.db"))
    await brain.boot()
    
    pregunta = "Hola, ¿quién eres y cuál es tu propósito?"
    print(f"\n[Usuario] > {pregunta}")
    try:
        response = await brain.process_input(pregunta, interface="cli")
        print(f"\n[nova26] > {response}")
    except Exception as e:
        print(f"\n[Error] > {e}")
        
    await brain.hibernate()
    print("\nBrain apagado correctamente.")

if __name__ == "__main__":
    asyncio.run(run_test())
