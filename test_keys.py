import asyncio
import os
from dotenv import load_dotenv
from llm.provider_manager import LLMProviderManager
import yaml

load_dotenv()

with open('config/default_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

async def test():
    manager = LLMProviderManager(config)
    messages = [{"role": "user", "content": "Hola, di 'prueba exitosa' brevemente."}]
    
    # Test Gemini
    print("Testing Gemini directly...")
    try:
        gemini = manager._get_provider('gemini')
        # force recreate client with env var if missing
        res = await gemini.chat(messages, 'simple')
        print("Gemini response:", res)
    except Exception as e:
        print("Gemini error:", e)

    # Test Deepseek
    print("\nTesting DeepSeek directly...")
    try:
        ds = manager._get_provider('deepseek')
        res = await ds.chat(messages, 'simple')
        print("DeepSeek response:", res)
    except Exception as e:
        print("DeepSeek error:", e)

if __name__ == "__main__":
    asyncio.run(test())
