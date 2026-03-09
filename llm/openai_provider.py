"""
OpenAI Provider
Uses OAuth Codex tokens stored in the database to authenticate against OpenAI API.
"""
import time
from openai import AsyncOpenAI
from core.oauth_manager import OAuthManager

class OpenAIProvider:
    def __init__(self, config: dict, db):
        self.config = config
        self.db = db
        self.client = None
        
    async def _init_client(self):
        """Lazy load and auth client using DB tokens."""
        if not self.client:
            oauth = OAuthManager(self.db)
            token = await oauth.get_openai_token()
            if not token:
                raise ValueError("No OpenAI Codex token found. Run `nova26-configure` first.")
            
            # OpenAI requires 'Bearer <token>' automatically placed by AsyncOpenAI
            self.client = AsyncOpenAI(api_key=token)

    async def chat(self, messages: list, complexity: str, task_model: str = None) -> dict:
        await self._init_client()
        
        # Priority 1: User selected model from dashboard (task_model)
        # Priority 2: Complexity mapping from config
        # Priority 3: Defaults
        
        model_id = task_model
        if not model_id:
            models = self.config.get('models', {})
            model_id = models.get('capable', 'gpt-4o')
            
            if complexity == 'trivial':
                model_id = models.get('fast', 'gpt-4o-mini')
            elif complexity == 'complex':
                model_id = models.get('reasoning', 'o1-preview')
            
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
