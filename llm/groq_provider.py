"""
Groq Provider
Fast inference via OpenAI compatibility layer.
"""
import os
import time
from openai import AsyncOpenAI

class GroqProvider:
    def __init__(self, config: dict):
        self.config = config
        api_key_env = config.get('api_key_env', 'GROQ_API_KEY')
        self.api_key = os.getenv(api_key_env)
        self.base_url = config.get('base_url', 'https://api.groq.com/openai/v1')
        self.client = None
        
    async def chat(self, messages: list, complexity: str) -> dict:
        if not self.client:
            if not self.api_key:
                raise ValueError("API Key not found.")
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
        # Select model based on complexity mapping in config
        models = self.config.get('models', {})
        model_id = models.get('capable', 'llama-3.3-70b-versatile')
        
        if complexity == 'trivial':
            model_id = models.get('fast', model_id)
        elif complexity == 'complex':
            model_id = models.get('reasoning', model_id)
            
        start_time = time.time()
        
        response = await self.client.chat.completions.create(
            messages=messages,
            model=model_id,
            temperature=0.7,
            max_tokens=2000
        )
        
        latency = int((time.time() - start_time) * 1000)
        
        return {
            'content': response.choices[0].message.content,
            'model': model_id,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'latency_ms': latency
        }
