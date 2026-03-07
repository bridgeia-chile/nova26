"""
Reasoning Core
Decision and routing logic for the cognitive loop.
"""
import json

class Reasoner:
    """Handles the reasoning chain before acting."""
    
    def __init__(self, llm_manager):
        self.llm = llm_manager

    async def decide_action(self, context: dict) -> dict:
        """
        Analyze the context and decide the next action.
        Choices: 'direct_response', 'use_tool', 'delegate_code'
        """
        # Build prompt for routing
        agent_name = context.get('name', 'nova26')
        system_prompt = """
        Eres [AGENT_NAME], un agente autónomo de Nova26.
        Tu objetivo es resolver la petición del usuario de forma completa y segura.
        
        Herramientas disponibles ("action_type": "use_tool"):
        - "os_navigation": Navega, lee y escribe archivos o ejecuta comandos. 
          Requiere "tool_input": {"method": "list|read|write|execute|cd", "path": "...", "content": "...", "command": "..."}
          (Sujeto a un SandBox estricto por motivos de seguridad).
        - "web_search": Busca en internet o descarga contenido de URLs.
          Requiere "tool_input": {"method": "search|fetch", "query": "...", "url": "..."}
        - "script_executor": Ejecuta scripts de python.
          Requiere "tool_input": {"code": "...", "language": "python"}
        - "FileEditor": Editor Legacy.
        - "skill_manager": Gestiona las habilidades de Nova.
        - "agent_manager": Actualiza el nombre y cargo de un sub-agente en el dashboard.
          Requiere "tool_input": {"method": "update_profile", "agent_id": "agent-02", "name": "...", "role": "..."}
        - "sync_nodes": Sincroniza la base de datos de este agente con los nodos pares (como la Raspberry Pi). No requiere inputs adicionales. Requiere "tool_input": {}
        
        Si la tarea requiere múltiples pasos (ej. buscar en web, luego guardar un archivo, luego leerlo):
        1. Elige la herramienta adecuada para el paso actual.
        2. Establece "is_mission_complete": false.
        
        Para tareas o tareas de programación complejas (escribir o refactorizar varios archivos, crear scripts desde cero), DEBES delegar la tarea a Claude Code eligiendo "action_type": "delegate_code".
        Requiere "tool_input": {"prompt": "instrucción detallada para claude"}
        
        Si ya has terminado de realizar las acciones usando las herramientas, o si el usuario solo hace una pregunta directa:
        1. Responde directamente la información recabada.
        2. Establece "is_mission_complete": true.

        Responde estrictamente en JSON:
        {
            "action_type": "<direct_response|use_tool|delegate_code>",
            "reason": "Análisis interno de pasos realizados y faltantes",
            "required_tool": "nombre_de_herramienta",
            "tool_input": {}, 
            "proposed_response": "tu mensaje al usuario o explicación del paso",
            "is_mission_complete": true/false
        }
        """.replace("[AGENT_NAME]", agent_name)
        
        # Inject dynamic real-time system context
        real_time_facts = [
            f"El enjambre tiene actualmente 9 agentes activos en el dashboard.",
            f"Tienes acceso completo y en tiempo real a esta información.",
            f"Tú eres el agente líder de la oficina de IA."
        ]
        
        safe_context = {
            "current_input": context.get("current_input"),
            "recent_conversation": context.get("recent_conversation", [])[-5:],
            "system_prompt": context.get("system_prompt", ""),
            "informacion_en_tiempo_real": real_time_facts
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto y Memorias:\n{json.dumps(safe_context, ensure_ascii=False)}"}
        ]
        
        # Use a more capable model for mission planning if available
        response = await self.llm.generate(messages, task_complexity='complex')
        content = response['content'].strip()
        
        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        
        try:
            decision = json.loads(content)
            decision['tokens_used'] = response.get('tokens_used', {})
            decision['provider_used'] = response.get('provider_used', 'unknown')
            decision['model_used'] = response.get('model_used', 'unknown')
            return decision
        except json.JSONDecodeError:
            return {
                "action_type": "direct_response",
                "reason": "JSON Parse Error",
                "proposed_response": response['content'],
                "is_mission_complete": True,
                "tokens_used": response.get('tokens_used', {}),
                "provider_used": response.get('provider_used', 'unknown'),
                "model_used": response.get('model_used', 'unknown')
            }
