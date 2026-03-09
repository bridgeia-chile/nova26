"""
LLM Provider Manager
Chain-of-fallback for LLM providers: Groq -> OpenRouter -> Ollama
"""
import logging
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

class LLMProviderManager:
    """Manages LLM fallback and execution."""
    
    def __init__(self, config: dict, db=None):
        self.config = config.get('llm', {})
        self.db = db
        self.providers = {}
        self.provider_chain = self.config.get('provider_chain', ['groq', 'openrouter', 'ollama'])
        
    def _get_provider(self, name: str):
        """Lazy load providers."""
        if name in self.providers:
            return self.providers[name]
            
        provider_config = self.config.get('providers', {}).get(name, {})
        if name == 'openai':
            from .openai_provider import OpenAIProvider
            self.providers[name] = OpenAIProvider(provider_config, self.db)
        elif name == 'gemini':
            from .gemini_provider import GeminiProvider
            self.providers[name] = GeminiProvider(provider_config, self.db)
        elif name in ['groq', 'openrouter', 'deepseek']:
            self.providers[name] = GroqProvider(provider_config)
        elif name == 'ollama':
            self.providers[name] = OllamaProvider(provider_config)
        return self.providers.get(name)

    async def generate(self, messages: list, task_complexity: str = 'simple', model: str = None) -> dict:
        """
        Attempts generation using the preferred provider.
        If a specific 'model' is requested, it tries to find the best provider for it.
        """
        final_chain = []
        
        # 1. If a specific model is requested, try to find its direct provider
        if model:
            provider_for_model = None
            m_lower = model.lower()
            if m_lower.startswith('gpt-') or m_lower.startswith('o1-'):
                provider_for_model = 'openai'
            elif m_lower.startswith('claude-'):
                provider_for_model = 'openrouter' # fallback or direct if we had it
            elif m_lower.startswith('gemini-'):
                provider_for_model = 'gemini'
            
            if provider_for_model:
                final_chain.append(provider_for_model)
        
        # 2. Add standard fallback chain
        paid_providers = ['deepseek', 'openai', 'gemini']
        free_chain = [p for p in self.provider_chain if p not in paid_providers]
        effective_chain = free_chain + ['gemini', 'deepseek']

        for p in effective_chain:
            if p not in final_chain:
                final_chain.append(p)

        for provider_name in final_chain:
            try:
                provider = self._get_provider(provider_name)
                if not provider:
                    continue
                
                # If the provider is OpenAI/Gemini/Ollama and we have a specific model, pass it
                chat_kwargs = {'messages': messages, 'complexity': task_complexity}
                if provider_name in ['openai', 'gemini', 'ollama'] and model:
                    chat_kwargs['task_model'] = model
                    
                response = await provider.chat(**chat_kwargs)
                content = response.get('content')
                if not content or not content.strip():
                    raise ValueError(f"Provider {provider_name} returned empty content.")
                    
                return {
                    'content': content,
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
