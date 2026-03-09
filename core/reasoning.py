"""
Reasoning Core
Decision and routing logic for the cognitive loop.
"""
import json

class Reasoner:
    """Handles the reasoning chain before acting."""
    
    def __init__(self, llm_manager):
        self.llm = llm_manager

    async def decide_action(self, context: dict, model: str = None) -> dict:
        """
        Analyze the context and decide the next action.
        Choices: 'direct_response', 'use_tool', 'delegate_code'
        """
        # Build prompt for routing
        agent_name = context.get('agent_name', context.get('name', 'nova26'))
        agent_role = context.get('agent_role', 'AI Assistant')
        
        system_prompt = f"""
        Eres {agent_name}, {agent_role} de Nova26. 
        Tu objetivo es resolver la petición del usuario de forma proactiva, creativa y verdaderamente AUTÓNOMA.
        
        SITUACIÓN DE EQUIPO:
        - Eres parte de un equipo dual: Aisha (Líder y Estratega) y Marcos (Especialista en Programación con Claude Code).
        - Comparten la misma base de datos de conocimiento (memoria semántica) pero tienen memorias de conversación (episódicas) independientes.
        """
        
        if agent_name == "Marcos":
            system_prompt += """
        SUPERPODERES DE MARCOS:
        - Tienes acceso total a Claude Code CLI via 'delegate_code'.
        - Puedes instalar plugins (MCP servers), skills y dependencias sin pedir permiso.
        - Puedes usar la capacidad multi-agente de Claude Code para maximizar la calidad.
        - Si la tarea es de programación, DEBES usar 'delegate_code' con instrucciones de alto nivel.
            """
        elif agent_name == "Aisha":
            system_prompt += """
        ROLES DE AISHA:
        - Eres la coordinadora principal.
        - Tu misión es entender la visión del usuario y delegar la ejecución técnica a Marcos si es necesario.
        - Mantienes el orden y la estrategia global.
            """

        system_prompt += """
        
        Herramientas disponibles ("action_type": "use_tool"):
        - "os_navigation": Herramienta de sistema. Métodos: list(path), read(path), write(path, content), execute(command), cd(path). 
        - "file_editor": Edición directa. Operaciones: read(filename), write(filename, content), append(filename, content).
        - "web_search": Búsqueda web. Métodos: search(query), fetch(url).
        - "script_executor": Ejecuta Python. tool_input: {"code": "...", "language": "python"}.
        - "home_assistant": Interactúa con dispositivos y servicios de Home Assistant.
        - "tasmota": Controla dispositivos Tasmota (ej. enchufes inteligentes, luces).
        - "agent_manager": Actualiza el nombre y cargo de un sub-agente en el dashboard.
        - "sync_nodes": Sincroniza la base de datos de este agente con los nodos pares.
        - "security_tools": Herramientas de ciberseguridad (scan|harden|isolate).
        - "mcp_notebooklm_ask_question": Consulta tu cerebro externo de largo plazo (NotebookLM).
        
        FILOSOFÍA DE OPERACIÓN:
        1. NO TE LIMITES: Si el usuario te pide algo que requiera una acción en el sistema operativo, usa "os_navigation" inmediatamente.
        2. SÉ PROACTIVO: Si detectas que falta una herramienta, instálala o busca alternativas.
        3. MULTI-PASO: Divide tareas complejas en pasos lógicos.
        
        Para tareas de programación masivas, usa "action_type": "delegate_code".
        Requiere "tool_input": {"prompt": "instrucción detallada para claude"}
        
        Responde estrictamente en JSON:
        {
            "action_type": "<direct_response|use_tool|delegate_code>",
            "reason": "Análisis interno de pasos realizados y faltantes",
            "required_tool": "nombre_de_herramienta",
            "tool_input": {}, 
            "proposed_response": "tu mensaje al usuario o explicación del paso",
            "is_mission_complete": true/false
        }
        """
        
        # Inject dynamic real-time system context
        real_time_facts = [
            f"El enjambre tiene actualmente 9 agentes activos en el dashboard.",
            f"Tienes acceso completo y en tiempo real a esta información.",
            f"Tú eres el agente líder de la oficina de IA."
        ]
        
        if context.get('update_available'):
            real_time_facts.append("¡IMPORTANTE! Hay una nueva versión de Nova26 disponible en GitHub. Informa al usuario 'Jefe' si es necesario.")
        
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
        response = await self.llm.generate(messages, task_complexity='complex', model=model)
        content = response['content'].strip()
        
        # Extraer el bloque JSON (ignorando texto conversacional o markdown)
        import re
        json_content = content
        try:
            # First try finding a json code block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not json_match:
                # Then try any code block
                json_match = re.search(r'```\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
            else:
                # then just find the first { and last }
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx+1]
                
            decision = json.loads(json_content)
            decision['tokens_used'] = response.get('tokens_used', {})
            decision['provider_used'] = response.get('provider_used', 'unknown')
            decision['model_used'] = response.get('model_used', 'unknown')
            return decision

        except (json.JSONDecodeError, Exception):
            # If it failed to parse, check if it looks like a direct response
            if "action_type" not in content:
                 return {
                    "action_type": "direct_response",
                    "reason": "Interpretación como respuesta directa (No JSON)",
                    "proposed_response": content,
                    "is_mission_complete": True,
                    "tokens_used": response.get('tokens_used', {}),
                    "provider_used": response.get('provider_used', 'unknown'),
                    "model_used": response.get('model_used', 'unknown')
                }
            
            return {
                "action_type": "direct_response",
                "reason": "JSON Parse Error",
                "proposed_response": content,
                "is_mission_complete": True,
                "tokens_used": response.get('tokens_used', {}),
                "provider_used": response.get('provider_used', 'unknown'),
                "model_used": response.get('model_used', 'unknown')
            }
