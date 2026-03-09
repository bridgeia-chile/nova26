"""
nova26 Brain - Loop cognitivo principal
Implementa el ciclo: Percibir -> Recordar -> Razonar -> Actuar -> Aprender
"""
import asyncio
import logging
from datetime import datetime

from memory.soul_db import SoulDB
from core.identity import Identity
from core.memory import MemoryManager
from core.resource_manager import ResourceBudget
from core.reasoning import Reasoner
from llm.provider_manager import LLMProviderManager
from core.sentry_monitor import SentryMonitor
from tools.security_tools import SecurityTools
from skills.skill_manager import SkillManager
from tools.tool_registry import ToolRegistry
from tools.mcp_client import MCPClientManager
from tools.notebooklm_helper import NotebookLMHelper

class NovaGravityBrain:
    """Orquestador principal del agente."""

    def __init__(self, soul_db_path: str):
        self.soul_path = soul_db_path
        self.db = SoulDB(soul_db_path)
        self.identity = Identity(self.db)
        self.memory = MemoryManager(self.db)
        self.resource_budget = ResourceBudget()
        
        # Will be fully initialized in boot()
        self.llm = None
        self.reasoner = None
        self.tools = None
        self.skills = None
        self.mcp_manager = None
        self.notebook_helper = NotebookLMHelper(self.memory)
        
        self.is_alive = False
        self.cycle_count = 0
        self.active_sessions = set()
        self.current_mission = "Idle"
        self.last_action = "Iniciando..."
        self.update_available = False
        self.sentry = SentryMonitor(soul_db_path)
        self.security_tools = SecurityTools()

    async def boot(self, config_dir: str = 'config'):
        """Secuencia de arranque."""
        print(f"[*] Iniciando cerebro de nova26...")
        await self.db.connect()
        
        # Ensure schema is up to date (apply new tables if any)
        await self.db._apply_schema()

        # Initialize Skill Manager
        from skills.skill_manager import SkillManager
        self.skills = SkillManager(self.db) # Initialize SkillManager here
        from core.oauth_manager import OAuthManager
        self.oauth_manager = OAuthManager(self.db)
        
        identity_state = await self.identity.load_or_create(config_dir)
        await self.identity.update_boot_stats()
        
        import yaml
        from pathlib import Path
        config_path = Path(config_dir) / 'default_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        self.llm = LLMProviderManager(config, self.db)
        self.reasoner = Reasoner(self.llm)
        
        # Initialize Tooling and MCP
        from tools.mcp_client import MCPClientManager
        from tools.tool_registry import ToolRegistry
        self.mcp_manager = MCPClientManager(self.db)
        self.tools = ToolRegistry(self.db, self.mcp_manager)
        await self.tools.load_from_db()

        # Initialize Claude Code Bridge
        from tools.claude_code_bridge import ClaudeCodeBridge
        self.claude_bridge = ClaudeCodeBridge(self.tools, self.mcp_manager)
        
        # Initialize P2P Tunnel Manager
        from core.tunnel_manager import TunnelManager
        self.tunnel = TunnelManager(self.soul_path, self)
        self.tunnel.start()

        # Auto-install skills missing recorded in DB
        await self.skills.auto_install_missing()
        
        # Initialize model configurations if empty
        await self._initialize_models_config()
        
        await self.db.log_evolution('boot', f"Booted identity: {identity_state['name']}")
        self.is_alive = True
        
        # Background update check
        async def check_updates_loop():
            from core.update_manager import UpdateManager
            updater = UpdateManager()
            while self.is_alive:
                self.update_available = updater.check_for_updates()
                await asyncio.sleep(3600) # Every hour manually for brain, or 600 for faster
        
        asyncio.create_task(check_updates_loop())
        
        # Background security monitoring
        async def sentry_monitor_loop():
            while self.is_alive:
                try:
                    await self.sentry.run_step()
                except Exception as e:
                    import logging
                    logging.error(f"Sentry loop error: {e}")
                await asyncio.sleep(60) # Passive check every 60 seconds
        
        asyncio.create_task(sentry_monitor_loop())
        
        return identity_state

    async def process_input(self, raw_input: str, interface: str = 'telegram') -> str:
        """Ciclo cognitivo completo para un input con bucle de misión autónomo."""
        if not self.is_alive:
            raise RuntimeError("Brain is not booted.")
            
        self.cycle_count += 1
        self.resource_budget.reset_cycle()
        session_id = f"session_{datetime.now().strftime('%Y%m%d')}"
        
        # 1. Perceive
        self.active_sessions.add(interface)
        self.current_mission = "Procesando..."
        self.last_action = f"Recibido input de {interface}"
        perception = await self._perceive(raw_input, session_id, interface)
        
        max_steps = 5
        current_step = 0
        is_complete = False
        final_response = ""

        # Bucle de Misión Autónomo (OpenGravity Pattern)
        # Identificamos si el mensaje es para un agente específico para usar su modelo preferido
        target_agent_id = "agent-01" # Default Aisha
        preferred_model = None
        
        # Detección de agente por nombre o prefijo
        lower_input = raw_input.lower()
        if "marcos" in lower_input and "aisha" not in lower_input:
            target_agent_id = "agent-02"
        elif "aisha" in lower_input:
            target_agent_id = "agent-01"
        elif raw_input.startswith("[Para "):
            try:
                # Formato: [Para agent-01]: mensaje
                parts = raw_input.split("]:", 1)
                if len(parts) > 1:
                    target_agent_id = parts[0].replace("[Para ", "").strip()
            except Exception as e:
                logging.error(f"Error parsing agent prefix: {e}")

        # Obtener configuración del agente seleccionado
        import sqlite3
        try:
            conn = sqlite3.connect(self.soul_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name, role, selected_model FROM sub_agents WHERE id = ?", (target_agent_id,))
            agent_row = cursor.fetchone()
            if agent_row:
                preferred_model = agent_row['selected_model']
                agent_name = agent_row['name']
                agent_role = agent_row['role']
            else:
                agent_name = "Nova Agent"
                agent_role = "AI Assistant"
            conn.close()
        except Exception as e:
            logging.error(f"Error fetching agent data: {e}")
            agent_name = "Nova Agent"
            agent_role = "AI Assistant"

        while not is_complete and current_step < max_steps:
            current_step += 1
            
            # 2. Remember (Filtramos por agente)
            context = await self._remember(perception, agent_id=target_agent_id)
            context['agent_name'] = agent_name
            context['agent_role'] = agent_role
            
            # 3. Reason
            decision = await self._reason(context, model=preferred_model)
            is_complete = decision.get("is_mission_complete", True)
            
            # Log token usage from reasoning
            tokens = decision.get("tokens_used", {})
            if isinstance(tokens, dict):
                p_tokens = tokens.get("prompt_tokens", 0)
                c_tokens = tokens.get("completion_tokens", 0)
                if p_tokens > 0 or c_tokens > 0:
                    model_used = decision.get("model_used", "unknown")
                    # En este momento, hardcodeado a agent-01 que es el principal (Core)
                    await self.memory.log_token_usage("agent-01", model_used, p_tokens, c_tokens)
            
            # 4. Act
            if is_complete:
                self.current_mission = "Idle"
                self.last_action = "Misión completada."
            else:
                self.last_action = f"Ejecutando: {decision.get('thought', 'Pensando...')[:30]}..."
                
            action_result = await self._act(decision)
            final_response = action_result.get('response', 'Error en paso.')

            # 5. Learn
            await self._learn(perception, decision, action_result)
            
            # Si la misión no ha terminado, inyectamos el resultado como nuevo input
            if not is_complete:
                perception["input_text"] = f"ACCION PREVIA: {decision.get('reason')}\nRESULTADO: {final_response}\nCONTINÚA CON EL SIGUIENTE PASO."

        # 6. Reflect (Cada N ciclos)
        if self.cycle_count % self.resource_budget.REFLECTION_INTERVAL == 0:
            await self._reflect()
            
        # Log assistant response to episodic (para el agente que respondió)
        await self.memory.add_episodic(session_id, 'assistant', final_response, interface, agent_id=target_agent_id)
        
        # Opcional: Respaldar en NotebookLM si la misión fue importante
        if is_complete:
             asyncio.create_task(self._backup_to_notebooklm())
             
        # Safety fallback
        if not final_response or not final_response.strip():
            final_response = "Lo siento, mi procesador cognitivo no generó una respuesta clara en este momento. Por favor, intenta de nuevo."
        
        # Check if the response looks like a raw technical dictionary string
        if final_response.startswith("{'") and "'exit_code'" in final_response:
            final_response = "Tuve un problema técnico al intentar ejecutar esa acción en tu equipo. Por favor, verifica si la herramienta está instalada o intenta de otra forma."
            
        return final_response

    async def _backup_to_notebooklm(self):
        """Respalda la memoria reciente en el cuaderno configurado."""
        try:
            # Obtener notebook_id de la configuración
            async with self.db.conn.execute("SELECT value FROM config WHERE key = 'notebooklm_backup_id'") as cursor:
                row = await cursor.fetchone()
                if row:
                    notebook_id = row[0]
                    await self.notebook_helper.backup_to_notebook(self, notebook_id)
        except Exception as e:
            logging.error(f"Falla en respaldo automático a NotebookLM: {e}")

    async def _initialize_models_config(self):
        """Populates the models_config table with default models if empty."""
        # Migration: Check if category column exists
        try:
            async with self.db.conn.execute("SELECT category FROM models_config LIMIT 1") as cursor:
                await cursor.fetchone()
        except Exception:
            # Column missing, add it
            await self.db.conn.execute("ALTER TABLE models_config ADD COLUMN category TEXT DEFAULT 'Direct API'")
            await self.db.conn.commit()

        async with self.db.conn.execute("SELECT COUNT(*) FROM models_config") as cursor:
            count = (await cursor.fetchone())[0]
            
        if count <= 25: # Re-seed to include ALL models
            await self.db.conn.execute("DELETE FROM models_config")
            
            default_models = [
                # Direct APIs
                ('openai:gpt-4o', 'openai', 'gpt-4o', 'Direct API', 0.7, 1),
                ('openai:gpt-4o-mini', 'openai', 'gpt-4o-mini', 'Direct API', 0.7, 1),
                ('openai:o3-mini', 'openai', 'o3-mini', 'Direct API', 0.7, 1),
                ('openai:gpt-codex-5.2', 'openai', 'gpt-codex-5.2', 'Direct API', 0.7, 1),
                ('openai:gpt-codex-5.3', 'openai', 'gpt-codex-5.3', 'Direct API', 0.7, 1),
                ('gemini:gemini-1.5-pro', 'gemini', 'gemini-1.5-pro', 'Direct API', 0.7, 1),
                ('gemini:gemini-1.5-flash', 'gemini', 'gemini-1.5-flash', 'Direct API', 0.7, 1),
                ('gemini:gemini-2.0-flash', 'gemini', 'gemini-2.0-flash', 'Direct API', 0.7, 1),
                ('gemini:gemini-2.0-pro-exp-02-05', 'gemini', 'gemini-2.0-pro-exp-02-05', 'Direct API', 0.7, 1),
                
                # Free Operators
                ('groq:llama-3.1-8b-instant', 'groq', 'llama-3.1-8b-instant', 'Operador Gratuito', 0.7, 1),
                ('groq:llama-3.3-70b-versatile', 'groq', 'llama-3.3-70b-versatile', 'Operador Gratuito', 0.7, 1),
                ('groq:mixtral-8x7b-32768', 'groq', 'mixtral-8x7b-32768', 'Operador Gratuito', 0.7, 1),
                ('groq:whisper-large-v3-turbo', 'groq', 'whisper-large-v3-turbo', 'Operador Gratuito', 0.7, 1),
                ('deepseek:deepseek-chat', 'deepseek', 'deepseek-chat', 'Operador Gratuito', 0.7, 1),
                ('deepseek:deepseek-reasoner', 'deepseek', 'deepseek-reasoner', 'Operador Gratuito', 0.7, 1),
                ('openrouter:google/gemini-2.0-flash-lite', 'openrouter', 'google/gemini-2.0-flash-lite-preview-02-05:free', 'Operador Gratuito', 0.7, 1),
                ('openrouter:deepseek/deepseek-chat:free', 'openrouter', 'deepseek/deepseek-chat:free', 'Operador Gratuito', 0.7, 1),
                
                # Ollama Local
                ('ollama:llama3.2:3b', 'ollama', 'llama3.2:3b', 'Ollama Local', 0.7, 1),
                ('ollama:qwen2.5-coder:7b', 'ollama', 'qwen2.5-coder:7b', 'Ollama Local', 0.7, 1),
                ('ollama:phi3:latest', 'ollama', 'phi3:latest', 'Ollama Local', 0.7, 1),
                ('ollama:nomic-embed-text', 'ollama', 'nomic-embed-text', 'Ollama Local', 0.7, 1),
                
                # Ollama Cloud (Simulado o vía OpenRouter/Local Tunnel)
                ('ollama-cloud:llama3.1:8b', 'ollama', 'llama3.1:8b', 'Ollama Cloud', 0.7, 1),
                ('ollama:marcos-adaptive', 'ollama', 'marcos-adaptive', 'Ollama Adaptive', 0.7, 1)
            ]
            await self.db.conn.executemany(
                "INSERT INTO models_config (id, provider, model_name, category, temperature, is_enabled) VALUES (?, ?, ?, ?, ?, ?)",
                default_models
            )
            await self.db.conn.commit()
            print("[+] Configuración de modelos expandida e inicializada.")

    async def _perceive(self, raw_input: str, session_id: str, interface: str) -> dict:
        """Log user input via memory manager and normalize."""
        # Podemos registrar el input del usuario para todos o para el agente detectado
        # Para simplicidad y siguiendo el requerimiento de "memoria propia", lo registramos para el agente activo
        # Pero Aisha (la coordinadora) podría registrarlo por defecto si no se detecta Marcos.
        target_agent = "agent-01"
        if "marcos" in raw_input.lower():
            target_agent = "agent-02"
            
        await self.memory.add_episodic(session_id, 'user', raw_input, interface, agent_id=target_agent)
        return {"input_text": raw_input, "session_id": session_id, "active_agent": target_agent}

    async def _remember(self, perception: dict, agent_id: str = 'agent-01') -> dict:
        """Busca memorias relevantes filtrando por el agente activo."""
        recent_episodic = await self.memory.get_recent_episodic(limit=10, agent_id=agent_id)
        top_semantic = await self.memory.search_semantic()
        return {
            "name": self.identity.state.get('name', 'Nova Team'),
            "current_input": perception["input_text"],
            "recent_conversation": recent_episodic,
            "semantic_knowledge": top_semantic,
            "system_prompt": self.identity.state.get('system_prompt', ''),
            "update_available": self.update_available
        }

    async def _reason(self, context: dict, model: str = None) -> dict:
        """Decide qué hacer."""
        return await self.reasoner.decide_action(context, model=model)

    async def _act(self, decision: dict) -> dict:
        """Ejecuta la acción usando herramientas reales."""
        action_type = decision.get("action_type")
        tool_name = str(decision.get("required_tool", "")).lower()
        tool_input = decision.get("tool_input", {})
        
        if action_type == "direct_response":
            return {"response": decision.get("proposed_response")}
            
        elif action_type == "use_tool":
            if tool_name == "script_executor":
                from tools.script_executor import ScriptExecutor
                executor = ScriptExecutor()
                code = tool_input.get("code")
                lang = tool_input.get("language", "python")
                res = await executor.execute(code, lang)
                stdout = res.get('stdout', '')
                stderr = res.get('stderr', '')
                error = res.get('error', '')
                return {"response": f"STDOUT: {stdout}\nSTDERR: {stderr}\nERROR: {error}"}
            
            elif tool_name == "skill_manager":
                method = tool_input.get("method")
                if method == "list":
                    md_skills = await self.skills.list_md_skills()
                    db_audit = await self.skills.audit_skills()
                    return {"response": f"Habilidades MD: {md_skills}\nHabilidades DB: {[s['skill_name'] for s in db_audit['missing']]}"}
                elif method == "create":
                    success = await self.skills.create_md_skill(tool_input.get("name"), tool_input.get("content"))
                    return {"response": "Habilidad creada exitosamente." if success else "Error creando habilidad."}
                elif method == "install":
                    # skill_data should be a dict with name, type, install_command, etc.
                    await self.skills.register_new_skill(tool_input.get("skill_data"))
                    return {"response": f"Habilidad registrada e instalación programada."}
                
            elif tool_name == "agent_manager":
                method = tool_input.get("method")
                if method == "update_profile":
                    agent_id = tool_input.get("agent_id")
                    name = tool_input.get("name")
                    role = tool_input.get("role")
                    if not agent_id or not name or not role:
                        return {"response": "Faltan parámetros (agent_id, name o role) para agent_manager."}
                    import sqlite3
                    try:
                        conn = sqlite3.connect(self.soul_path)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE sub_agents SET name=?, role=? WHERE id=?", (name, role, agent_id))
                        conn.commit()
                        conn.close()
                        return {"response": f"Perfil actualizado correctamente para {agent_id}: Nombre='{name}', Cargo='{role}'"}
                    except Exception as e:
                        return {"response": f"Error actualizando perfil en BD: {e}"}
                else:
                    return {"response": "Método de agent_manager no reconocido."}

            elif tool_name == "home_assistant":
                import os
                from tools.home_assistant import HomeAssistantTool
                ha_url = os.getenv("HA_URL")
                ha_token = os.getenv("HA_TOKEN")
                if not ha_url or not ha_token:
                    return {"response": "Error: HA_URL o HA_TOKEN no están configurados en el entorno."}
                
                ha_tool = HomeAssistantTool(ha_url, ha_token)
                method = tool_input.get("method")
                if method == "get_state":
                    res = await ha_tool.get_state(tool_input.get("entity_id", ""))
                elif method == "call_service":
                    res = await ha_tool.call_service(
                        tool_input.get("domain", ""),
                        tool_input.get("service", ""),
                        tool_input.get("service_data", {})
                    )
                elif method == "check_api":
                    is_ok = await ha_tool.check_api()
                    res = {"status": "Online" if is_ok else "Offline o Error de Token"}
                else:
                    res = {"error": "Método de home_assistant no reconocido."}
                return {"response": str(res)}

            elif tool_name == "sync_nodes":
                try:
                    status = self.tunnel.get_status()
                    target = status.get('target_host')
                    connections = status.get('active_connections', [])
                    
                    if not target and not connections:
                        return {"response": "La red P2P (Túnel) no está configurada o no hay nadie conectado."}
                    
                    msg = f"Red Nova P2P:\nHost Objetivo: {target or 'Ninguno'}\nConexiones Activas: {len(connections)} ({', '.join(connections) if connections else 'N/A'})"
                    return {"response": msg}
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    return {"response": f"Error verificando túnel: {e}"}
                
            elif tool_name in ["fileeditor", "file_editor"]:
                from tools.file_editor import FileEditor
                editor = FileEditor()
                filename = tool_input.get("filename") or tool_input.get("path") or tool_input.get("file_path")
                if not filename:
                    return {"response": "ERROR: 'filename' es requerido para file_editor."}
                res = editor.execute(
                    tool_input.get("operation", "read"),
                    filename,
                    tool_input.get("content")
                )
                return {"response": res}

            elif tool_name == "audio_tools":
                from tools.audio_tools import AudioTools
                audio = AudioTools()
                method = tool_input.get("method")
                if method == "transcribe":
                    res = await audio.transcribe(tool_input.get("file_path"))
                    return {"response": res}
                elif method == "speak":
                    res = await audio.text_to_speech(tool_input.get("text"), tool_input.get("voice_id"))
                    return {"response": res}
                elif method == "list_voices":
                    res = await audio.list_voices()
                    return {"response": str(res)}
                    
            elif tool_name == "os_navigation":
                from tools.os_navigation import OSNavigation
                # We initialize with a strict default (current working directory of nova26)
                navigator = OSNavigation()
                path = tool_input.get("path") or tool_input.get("filename") or tool_input.get("file_path")
                if method == "list":
                    res = navigator.list_directory(path or ".")
                elif method == "read":
                    if not path: return {"response": "ERROR: 'path' es requerido para read."}
                    res = navigator.read_file(path)
                elif method == "write":
                    if not path: return {"response": "ERROR: 'path' es requerido para write."}
                    res = navigator.write_file(path, tool_input.get("content", ""))
                elif method == "execute":
                    cmd = tool_input.get("command") or tool_input.get("code")
                    if not cmd: return {"response": "ERROR: 'command' es requerido para execute."}
                    res = navigator.execute_command(cmd)
                elif method == "cd":
                    if not path: return {"response": "ERROR: 'path' es requerido para cd."}
                    res = navigator.change_directory(path)
                elif method == "network_ping_scan":
                    res = navigator.network_ping_scan(tool_input.get("subnet", "192.168.1"))
                else:
                    res = {"error": "Método de OS Navigation no reconocido."}
                return {"response": str(res)}
                
            elif tool_name == "web_search":
                from tools.web_search import WebSearch
                ws = WebSearch()
                method = tool_input.get("method")
                if method == "search":
                    res = ws.search_duckduckgo(tool_input.get("query"))
                elif method == "fetch":
                    res = ws.fetch_url(tool_input.get("url"))
                else:
                    res = {"error": "Método de Web Search no reconocido."}
                return {"response": str(res)}
            
            elif tool_name == "security_tools":
                method = tool_input.get("method")
                if method == "scan":
                    return {"response": self.security_tools.scan_system()}
                elif method == "harden":
                    return {"response": self.security_tools.harden_system()}
                elif method == "isolate":
                    return {"response": self.security_tools.isolate_threat(tool_input.get("path"))}
                else:
                    return {"response": f"Método {method} no reconocido en security_tools."}

            elif tool_name == "home_assistant":
                from tools.home_assistant import HomeAssistantTool
                ha = HomeAssistantTool()
                method = tool_input.get("method")
                if method == "get_states":
                    res = await ha.get_states(tool_input.get("entity_id"))
                elif method == "call_service":
                    res = await ha.call_service(
                        tool_input.get("domain"),
                        tool_input.get("service"),
                        tool_input.get("service_data")
                    )
                elif method == "check":
                    res = await ha.check_api()
                else:
                    res = {"error": "Método de Home Assistant no reconocido."}
                return {"response": str(res)}

            elif tool_name == "tasmota":
                from tools.tasmota import TasmotaTool
                tasmota = TasmotaTool()
                method = tool_input.get("method")
                ip = tool_input.get("ip")
                if method == "send_command":
                    res = await tasmota.send_command(ip, tool_input.get("cmnd"))
                elif method == "rf_send":
                    res = await tasmota.rf_send(ip, tool_input.get("rf_code"))
                elif method == "toggle":
                    res = await tasmota.toggle(ip, tool_input.get("power_index", 1))
                elif method == "set_power":
                    res = await tasmota.set_power(ip, tool_input.get("state"), tool_input.get("power_index", 1))
                else:
                    res = {"error": "Método de Tasmota no reconocido."}
                return {"response": str(res)}
            
            elif tool_name.startswith("mcp_stitchmcp_"):
                # Bridge to internal Stitch tools
                # Since we are running in an environment with StitchMCP, 
                # we can use the registry to call it if it's connected, 
                # or provide a specific bridge.
                try:
                    # In this architecture, we check if the MCP manager has it
                    # If not found, we use a mock for demonstration or a direct bridge
                    method_name = tool_name.replace("mcp_stitchmcp_", "")
                    res = await self.mcp_manager.execute_tool("StitchMCP", method_name, tool_input)
                    
                    # Log usage for generation/edit operations
                    if "error" not in res and method_name in ("generate_screen_from_text", "edit_screens"):
                        try:
                            import sqlite3
                            conn = sqlite3.connect(self.soul_path)
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO stitch_usage (agent_id, operation, project_id) VALUES (?, ?, ?)",
                                ("agent-05", method_name, tool_input.get('projectId', 'unknown'))
                            )
                            conn.commit()
                            conn.close()
                        except Exception as log_err:
                            logging.error(f"Error logging Stitch usage: {log_err}")
                            
                    return {"response": str(res)}
                except Exception as e:
                    return {"response": f"Error ejecutando Stitch: {e}"}
                
            return {"response": f"Herramienta {tool_name} no disponible aún."}
            
        elif action_type == "delegate_code":
            prompt = tool_input.get("prompt") or decision.get("reason")
            workdir = tool_input.get("workdir", ".")
            res = await self.claude_bridge.delegate_task(prompt, workdir)
            return {"response": str(res.get('result', res.get('error', 'Error en delegación.')))}
            
        return {"response": "Acción no reconocida."}

    async def _learn(self, perception: dict, decision: dict, action_result: dict):
        """Extrae conocimiento."""
        pass

    async def _reflect(self):
        """Auto-evaluación periódica."""
        await self.db.log_evolution('reflection', 'Consolidating memories and optimizing resources.')

    async def hibernate(self):
        """Apagar limpiamente."""
        await self.db.log_evolution('shutdown', 'Hibernating Brain.')
        await self.db.close()
        self.is_alive = False
        
    async def restore(self):
        """Hooks para restaurar en una nueva maquina."""
        await self.boot()
