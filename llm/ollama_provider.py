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
        from core.hardware import is_gpu_available
        
        # Determine the primary model to use
        model_id = task_model if task_model else self.models.get('default', 'llama3.2:3b')
        
        # Logic for Marcos adaptive model
        is_marcos_adaptive = (model_id == "ollama:marcos-adaptive")
        if is_marcos_adaptive:
            if is_gpu_available():
                # GPU detected: Use cloud model (e.g., llama3.1:8b)
                model_id = self.models.get('cloud', 'llama3.1:8b')
            else:
                # No GPU: Use cloud free model (e.g., openrouter free models or similar)
                # For Ollama provider specifically, we might use a lighter cloud model if available
                model_id = self.models.get('cloud_free', 'llama3.1:8b') # Defaulting to same for now or specific free tag
                
        if not task_model and complexity == 'code' and not is_marcos_adaptive:
            model_id = self.models.get('code', model_id)
            
        start_time = time.time()
        
        try:
            return await self._execute_request(model_id, messages, start_time)
        except Exception as e:
            # Fallback logic: 
            # 1. If it's the marcos-adaptive cloud model, fall back to local coder
            # 2. If it's any other "cloud" model and it fails, try the local coder model
            is_cloud = (model_id and "-cloud" in model_id.lower()) or is_marcos_adaptive
            
            if is_cloud:
                fallback_model = self.models.get('code', 'qwen2.5-coder:7b')
                logging.warning(f"Ollama cloud/adaptive model {model_id} failed: {str(e)}. Falling back to {fallback_model}...")
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
