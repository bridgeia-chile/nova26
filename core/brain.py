"""
nova26 Brain - Loop cognitivo principal
Implementa el ciclo: Percibir -> Recordar -> Razonar -> Actuar -> Aprender
"""
import asyncio
from datetime import datetime

from memory.soul_db import SoulDB
from core.identity import IdentityManager
from core.memory import MemoryManager
from core.resource_manager import ResourceBudget
from core.reasoning import Reasoner
from llm.provider_manager import LLMProviderManager

class NovaGravityBrain:
    """Orquestador principal del agente."""

    def __init__(self, soul_db_path: str):
        self.soul_path = soul_db_path
        self.db = SoulDB(soul_db_path)
        self.identity = IdentityManager(self.db)
        self.memory = MemoryManager(self.db)
        self.resource_budget = ResourceBudget()
        
        self.llm = None
        self.reasoner = None
        self.tools = None
        self.skills = None
        
        self.is_alive = False
        self.cycle_count = 0
        self.active_sessions = set()
        self.current_mission = "Idle"
        self.last_action = "Iniciando..."
        self.update_available = False

    async def boot(self, config_dir: str = 'config'):
        """Secuencia de arranque."""
        print(f"[*] Iniciando cerebro de nova26...")
        await self.db.connect()
        
        # Initialize Skill Manager
        from skills.skill_manager import SkillManager
        self.skills = SkillManager(self.db)

        # Initialize OAuth Manager
        from core.oauth_manager import OAuthManager
        self.oauth_manager = OAuthManager(self.db)
        
        identity_state = await self.identity.load_or_create(config_dir)
        await self.identity.update_boot_stats()
        
        import yaml
        from pathlib import Path
        config_path = Path(config_dir) / 'default_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        self.llm = LLMProviderManager(config)
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
        
        # Auto-install skills missing recorded in DB
        await self.skills.auto_install_missing()
        
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
        while not is_complete and current_step < max_steps:
            current_step += 1
            
            # 2. Remember
            context = await self._remember(perception)
            
            # 3. Reason
            decision = await self._reason(context)
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
            
        # Log assistant response to episodic
        await self.memory.add_episodic(session_id, 'assistant', final_response, interface)
        
        return final_response

    async def _perceive(self, raw_input: str, session_id: str, interface: str) -> dict:
        """Log user input via memory manager and normalize."""
        await self.memory.add_episodic(session_id, 'user', raw_input, interface)
        return {"input_text": raw_input, "session_id": session_id}

    async def _remember(self, perception: dict) -> dict:
        """Busca memorias relevantes."""
        recent_episodic = await self.memory.get_recent_episodic(limit=10)
        top_semantic = await self.memory.search_semantic()
        return {
            "name": self.identity.state.get('name', 'nova26'),
            "current_input": perception["input_text"],
            "recent_conversation": recent_episodic,
            "semantic_knowledge": top_semantic,
            "system_prompt": self.identity.state.get('system_prompt', ''),
            "update_available": self.update_available
        }

    async def _reason(self, context: dict) -> dict:
        """Decide qué hacer."""
        return await self.reasoner.decide_action(context)

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

            elif tool_name == "sync_nodes":
                try:
                    from core.node_sync import NodeSynchronizer
                    import asyncio
                    sync = NodeSynchronizer(self.soul_path)
                    peers = sync.get_known_peers()
                    
                    if not peers:
                        return {"response": "No tienes configurada la IP de ningún nodo clon en variable PEER_NODES para sincronizar."}
                    
                    results = []
                    for peer in peers:
                        # Pull_from_peer is async, need to await it
                        res = await sync.pull_from_peer(peer)
                        if res.get('status') == 'success':
                            s = res.get('stats', {})
                            results.append(f"Clon ubicado en {peer}: Éxito (Importados: {s.get('episodic')} episodios, {s.get('semantic')} verdades)")
                        else:
                            results.append(f"Clon ubicado en {peer}: Falló ({res.get('message')})")
                    
                    return {"response": "\n".join(results)}
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    return {"response": f"Error fatal sincronizando: {e}"}
                
            elif tool_name == "FileEditor" or tool_name == "file_editor":
                from tools.file_editor import FileEditor
                editor = FileEditor()
                res = editor.execute(
                    tool_input.get("operation", "read"),
                    tool_input.get("filename"),
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
                method = tool_input.get("method")
                if method == "list":
                    res = navigator.list_directory(tool_input.get("path", "."))
                elif method == "read":
                    res = navigator.read_file(tool_input.get("path"))
                elif method == "write":
                    res = navigator.write_file(tool_input.get("path"), tool_input.get("content"))
                elif method == "execute":
                    res = navigator.execute_command(tool_input.get("command"))
                elif method == "cd":
                    res = navigator.change_directory(tool_input.get("path"))
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
            
            elif tool_name.startswith("mcp_stitchmcp_"):
                # Bridge to internal Stitch tools
                # Since we are running in an environment with StitchMCP, 
                # we can use the registry to call it if it's connected, 
                # or provide a specific bridge.
                try:
                    # In this architecture, we check if the MCP manager has it
                    # If not found, we use a mock for demonstration or a direct bridge
                    res = await self.mcp_manager.execute_tool("StitchMCP", tool_name.replace("mcp_stitchmcp_", ""), tool_input)
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
