"""
Resource Manager 
Gestion eficiente de recursos estilo PicoClaw.
"""

class ResourceBudget:
    """
    Controla el gasto de recursos por ciclo y globalmente.
    - Tokens LLM por ciclo (límite configurable)
    - Llamadas API por minuto
    - Uso de memoria RAM
    - Tiempo de CPU
    """

    MAX_TOKENS_PER_CYCLE = 2000    # Respuestas concisas
    MAX_CONTEXT_TOKENS = 4000      # Contexto compacto
    MAX_API_CALLS_PER_MIN = 10     # Rate limiting propio
    MEMORY_CACHE_SIZE_MB = 50      # Cache en RAM limitado
    REFLECTION_INTERVAL = 10       # Reflexionar cada N ciclos
    MEMORY_DECAY_DAYS = 30         # Decaer memorias no accedidas

    def __init__(self):
        self.tokens_used_this_cycle = 0
        self.api_calls_this_minute = 0
        self.active_tools = 0

    def reset_cycle(self):
        """Reset limits for a new reasoning cycle."""
        self.tokens_used_this_cycle = 0

    def can_spend_tokens(self, amount: int) -> bool:
        """¿Hay presupuesto de tokens disponible?"""
        return (self.tokens_used_this_cycle + amount) <= self.MAX_TOKENS_PER_CYCLE
        
    def spend_tokens(self, amount: int):
        """Consume token budget for the current cycle."""
        self.tokens_used_this_cycle += amount

    def select_model_for_task(self, task_complexity: str) -> dict:
        """
        Selecciona el modelo más eficiente para la tarea:
        - trivial: llama-3.1-8b via Groq (gratis, ultra rápido)
        - simple: llama-3.3-70b via Groq (gratis, capaz)
        - complex: deepseek-r1 via OpenRouter o Claude via API
        - code: Claude Code via MCP (sub-agente)
        - local_fallback: modelo local via Ollama
        """
        model_map = {
            'trivial': {
                'provider': 'groq',
                'model': 'llama-3.1-8b-instant',
                'max_tokens': 500
            },
            'simple': {
                'provider': 'groq',
                'model': 'llama-3.3-70b-versatile',
                'max_tokens': 1500
            },
            'complex': {
                'provider': 'openrouter',
                'model': 'deepseek/deepseek-r1',
                'max_tokens': 4000
            },
            'code': {
                'provider': 'claude_code_mcp',
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 8000
            },
            'local_fallback': {
                'provider': 'ollama',
                'model': 'llama3.2:3b',
                'max_tokens': 2000
            }
        }
        return model_map.get(task_complexity, model_map['simple'])
