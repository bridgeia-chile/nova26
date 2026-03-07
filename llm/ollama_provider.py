"""
Ollama Provider
Local offline fallback inference.
"""
import httpx
import time

class OllamaProvider:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.models = config.get('models', {})
        
    async def chat(self, messages: list, complexity: str) -> dict:
        model_id = self.models.get('default', 'llama3.2:3b')
        if complexity == 'code':
            model_id = self.models.get('code', model_id)
            
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model_id,
                    "messages": messages,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
        latency = int((time.time() - start_time) * 1000)
        
        return {
            'content': data['message']['content'],
            'model': model_id,
            'usage': {
                'prompt_tokens': data.get('prompt_eval_count', 0),
                'completion_tokens': data.get('eval_count', 0),
                'total_tokens': data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
            },
            'latency_ms': latency
        }
