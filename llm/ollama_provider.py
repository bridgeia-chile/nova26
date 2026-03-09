"""
Ollama Provider
Local offline fallback inference.
"""
import httpx
import time
import logging

class OllamaProvider:
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.models = config.get('models', {})
        
    async def chat(self, messages: list, complexity: str, task_model: str = None) -> dict:
        # Determine the primary model to use
        model_id = task_model if task_model else self.models.get('default', 'llama3.2:3b')
        if not task_model and complexity == 'code':
            model_id = self.models.get('code', model_id)
            
        start_time = time.time()
        
        try:
            return await self._execute_request(model_id, messages, start_time)
        except Exception as e:
            # Fallback logic: If it's a "cloud" model and it fails, try the local coder model
            if model_id and "-cloud" in model_id.lower():
                fallback_model = self.models.get('code', 'qwen2.5-coder:7b')
                logging.warning(f"Ollama cloud model {model_id} failed: {str(e)}. Falling back to {fallback_model}...")
                return await self._execute_request(fallback_model, messages, start_time)
            raise e

    async def _execute_request(self, model_id, messages, start_time):
        async with httpx.AsyncClient() as client:
            # Use a short connect timeout to fail fast if service is down, 
            # but keep a long total timeout for slow inference.
            timeout = httpx.Timeout(120.0, connect=5.0)
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model_id,
                    "messages": messages,
                    "stream": False
                },
                timeout=timeout
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
