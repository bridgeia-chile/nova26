import asyncio
import os
import yaml
from dotenv import load_dotenv
from llm.provider_manager import LLMProviderManager

load_dotenv()

async def test_fallback():
    with open('config/default_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    manager = LLMProviderManager(config)
    messages = [{"role": "user", "content": "Di hola y evalúa tu capacidad."}]
    
    # Let's inspect the effective chain directly just to be sure
    paid_providers = ['deepseek', 'openai', 'gemini']
    free_chain = [p for p in manager.provider_chain if p not in paid_providers]
    effective_chain = free_chain + ['gemini', 'deepseek']
    final_chain = []
    for p in effective_chain:
        if p not in final_chain:
            final_chain.append(p)
            
    print("Orden de Fallback configurado:", final_chain)
    print("Iniciando generación (esto probará los proveedores en orden)...\n")
    
    try:
        result = await manager.generate(messages, 'simple')
        print(f"\nGeneración Exitosa.")
        print(f"Proveedor Utilizado: {result.get('provider_used')}")
        print(f"Modelo Utilizado: {result.get('model_used')}")
        print(f"Respuesta: {result.get('content')}")
        print(f"Latencia: {result.get('latency_ms')}ms")
    except Exception as e:
        print(f"\nTodas las opciones fallaron. Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fallback())
