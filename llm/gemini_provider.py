import aiohttp
import json
import time
import logging
from core.oauth_manager import OAuthManager

class GeminiProvider:
    """Google Gemini LLM Provider using OAuth tokens."""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.oauth_manager = OAuthManager(db)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def chat(self, messages: list, complexity: str, task_model: str = None) -> dict:
        token = await self.oauth_manager.get_google_token()
        if not token:
            raise ValueError("Google Gemini no está autenticado. Usa 'nova26-configure'.")

        # Prioridad de modelo
        model_id = task_model
        if not model_id:
            models = self.config.get('models', {})
            model_id = models.get('capable', 'gemini-1.5-pro')
            if complexity == 'trivial':
                model_id = models.get('fast', 'gemini-1.5-flash')

        start_time = time.time()
        
        # Convert messages to Gemini format (contents/parts)
        contents = []
        for msg in messages:
            if msg['role'] == "system":
                # System prompt handling (Gemini 1.5 style) via system_instruction
                continue 
            
            role = "user" if msg['role'] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg['content']}]
            })

        # Correct endpoint: generateContent
        url = f"{self.api_url}/{model_id}:generateContent"
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }

        # If there's a system message, add it as system_instruction
        system_msgs = [m['content'] for m in messages if m['role'] == 'system']
        if system_msgs:
            payload["system_instruction"] = {
                "parts": [{"text": "\n".join(system_msgs)}]
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logging.error(f"Gemini API Error: {resp.status} - {error_text}")
                        raise Exception(f"Error de Gemini: {resp.status}")
                    
                    result = await resp.json()
                    
                    # Parse response
                    candidates = result.get('candidates', [])
                    if not candidates:
                        raise Exception("Gemini no devolvió candidatos de respuesta.")
                        
                    text = candidates[0]['content']['parts'][0]['text']
                    
                    return {
                        "content": text,
                        "model": model_id,
                        "usage": result.get('usageMetadata', {}),
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
            except Exception as e:
                logging.error(f"Error calling Gemini: {e}")
                raise
