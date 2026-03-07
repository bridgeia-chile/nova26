"""
LLM Provider Manager
Chain-of-fallback for LLM providers: Groq -> OpenRouter -> Ollama
"""
import logging
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider

class LLMProviderManager:
    """Manages LLM fallback and execution."""
    
    def __init__(self, config: dict):
        self.config = config.get('llm', {})
        self.providers = {}
        self.provider_chain = self.config.get('provider_chain', ['groq', 'openrouter', 'ollama'])
        
    def _get_provider(self, name: str):
        """Lazy load providers."""
        if name in self.providers:
            return self.providers[name]
            
        provider_config = self.config.get('providers', {}).get(name, {})
        if name in ['groq', 'openrouter', 'openai', 'deepseek', 'gemini']:
            self.providers[name] = GroqProvider(provider_config)
        elif name == 'ollama':
            self.providers[name] = OllamaProvider(provider_config)
        return self.providers.get(name)

    async def generate(self, messages: list, task_complexity: str = 'simple') -> dict:
        """
        Attempts generation using the preferred provider.
        Cascades if failures occur, prioritizing free providers first,
        and using paid providers (like DeepSeek) as last resort.
        """
        paid_providers = ['deepseek', 'openai', 'gemini']
        free_chain = [p for p in self.provider_chain if p not in paid_providers]
        
        # El usuario pidió el siguiente orden estricto de fallback:
        # 1. Gratuitos (groq, openrouter, ollama)
        # 2. Gemini
        # 3. DeepSeek (última instancia)
        effective_chain = free_chain + ['gemini', 'deepseek']

        # Deduplicar preservando el orden
        final_chain = []
        for p in effective_chain:
            if p not in final_chain:
                final_chain.append(p)

        for provider_name in final_chain:
            try:
                provider = self._get_provider(provider_name)
                if not provider:
                    continue
                    
                response = await provider.chat(messages, task_complexity)
                return {
                    'content': response['content'],
                    'provider_used': provider_name,
                    'model_used': response.get('model'),
                    'tokens_used': response.get('usage', {}),
                    'latency_ms': response.get('latency_ms')
                }
            except Exception as e:
                import traceback
                error_msg = str(e)
                print(f"!!! Provider {provider_name} EXACT ERROR !!!")
                print(error_msg)
                
                # If it's a critical auth error, we might want to log it distinctly
                if "API Key not found" in error_msg or "401" in error_msg:
                    logging.error(f"Provider {provider_name} authentication failed: {error_msg}")
                else:
                    logging.warning(f"Provider {provider_name} failed: {error_msg}. Falling back.")
                continue
                
        raise RuntimeError("All LLM Providers Failed.")
