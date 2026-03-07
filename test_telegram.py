import asyncio
from interfaces.telegram_bot import TelegramInterface

async def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token or token == "tu_token_de_botfather":
        print("ERROR: Token de telegram falso o ausente. Verifica tu .env")
        return
        
    print(f"Probando token: {token[:8]}...")
    
    # Init mockup interface relying on proper Brain logic
    from core.brain import NovaGravityBrain
    brain = NovaGravityBrain("nova26.db")
    
    tg = TelegramInterface(brain)
    
    try:
        print("Iniciando Poll...")
        await tg.start()
        print("Poll iniciado correctamente en background. Esperando 10 segundos para ver si hay errores...")
        await asyncio.sleep(10)
        print("Test Finalizado Sin Errores.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
