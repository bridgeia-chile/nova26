"""
API Server
A minimalistic local FastAPI server to allow external tools to send webhooks or interact.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import os

class APIServer:
    def __init__(self, brain):
        self.brain = brain
        self.app = FastAPI(title="nova26 API", version="1.0.0")
        self.setup_routes()
        
        # Mount static files
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
        if os.path.exists(static_path):
            self.app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    def setup_routes(self):
        @self.app.get("/api/v1/status")
        async def get_status():
            try:
                import psutil
                process = psutil.Process(os.getpid())
                mem_info = process.memory_info().rss / (1024 * 1024) # MB
                cpu_usage = psutil.cpu_percent(interval=None) # Get last sample
                
                # Fetch CPU Temperature safely
                cpu_temp = "N/A"
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps and 'coretemp' in temps:
                        cpu_temp = f"{temps['coretemp'][0].current}°C"
                    elif temps:
                        first_key = list(temps.keys())[0]
                        cpu_temp = f"{temps[first_key][0].current}°C"
                
                # Fetch GPU hardware safely using pynvml
                gpu_vram = "N/A"
                gpu_temp = "N/A"
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    gpu_vram = f"{info.used / (1024**3):.1f} GB"
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    gpu_temp = f"{temp}°C"
                except Exception:
                    pass

                # Get DB size
                db_size_bytes = 0
                soul_path = getattr(self.brain, 'soul_path', 'nova_soul.db')
                if os.path.exists(soul_path):
                    db_size_bytes = os.path.getsize(soul_path)
                db_size_kb = db_size_bytes / 1024

                # Extraer agentes y tokens de la base de datos
                agents = []
                import sqlite3
                conn = sqlite3.connect(soul_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT id, name, role, selected_model, status FROM sub_agents")
                db_agents = cursor.fetchall()

                for row in db_agents:
                    agent_id = row['id']
                    
                    # Calculate tokens
                    cursor.execute("SELECT SUM(total_tokens) as t_tokens FROM token_usage WHERE agent_id=?", (agent_id,))
                    t_row = cursor.fetchone()
                    total_tokens = t_row['t_tokens'] if t_row and t_row['t_tokens'] else 0
                    
                    is_core = (agent_id == 'agent-01')
                    
                    agents.append({
                        "id": agent_id,
                        "name": row['name'],
                        "model": row['selected_model'],
                        "ram": f"{int(mem_info)} MB" if is_core else "12 MB",
                        "vram": gpu_vram if is_core else "0 GB",
                        "cpu": f"{cpu_usage}%" if is_core else "0.1%",
                        "cpu_temp": cpu_temp if is_core else "N/A",
                        "gpu_temp": gpu_temp if is_core else "N/A",
                        "tokens": total_tokens,
                        "task": getattr(self.brain, 'current_mission', 'Idle') if is_core else row['role'],
                        "detail": getattr(self.brain, 'last_action', 'Esperando comandos...') if is_core else "Activo",
                        "status": "active" if self.brain.is_alive else "offline" if is_core else row['status']
                    })

                conn.close()
                sorted_agents = sorted(agents, key=lambda x: x['id'])

                # Prepare global system metrics
                system_metrics = {
                    "cpu_usage": f"{cpu_usage}%",
                    "ram_usage": f"{int(mem_info)} MB",
                    "vram_usage": gpu_vram
                }

                # Calculate Stitch Usage
                stitch_usage_monthly = 0
                try:
                    conn = sqlite3.connect(self.brain.soul_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM stitch_usage WHERE timestamp > date('now','start of month')")
                    stitch_usage_monthly = cursor.fetchone()[0]
                    conn.close()
                except Exception as e:
                    logging.error(f"Error calculating Stitch usage: {e}")

                return {
                    "agents": sorted_agents,
                    "db_size": f"{db_size_kb:.1f} KB" if db_size_kb < 1024 else f"{(db_size_kb/1024):.1f} MB",
                    "sessions_count": len(getattr(self.brain, 'active_sessions', [])),
                    "system_metrics": system_metrics,
                    "update_available": getattr(self.brain, 'update_available', False),
                    "stitch_usage_monthly": stitch_usage_monthly
                }
            except Exception as e:
                import traceback
                logging.error(f"Error in status endpoint: {traceback.format_exc()}")
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/interact")
        async def interact(request: Request):
            data = await request.json()
            user_input = data.get("text", "")
            
            try:
                response = await self.brain.process_input(user_input, interface='api')
                return {"status": "success", "response": response}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.get("/api/v1/models")
        async def get_models():
            try:
                available_models = [
                    "Llama-3.3-70b", "Llama-3.2-1b", "Llama-3.2-3b",
                    "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet",
                    "gemini-pro", "gemini-1.5-flash", "deepseek-coder",
                    "mixtral-8x7b", "gemma-7b", "claude_code"
                ]
                return {"status": "success", "models": available_models}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/agents/{agent_id}/model")
        async def set_agent_model(agent_id: str, request: Request):
            try:
                data = await request.json()
                new_model = data.get("model")
                if not new_model:
                    return {"status": "error", "message": "No model provided"}
                
                import sqlite3
                import os
                soul_path = getattr(self.brain, 'soul_path', 'nova_soul.db')
                conn = sqlite3.connect(soul_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE sub_agents SET selected_model = ? WHERE id = ?", (new_model, agent_id))
                conn.commit()
                conn.close()
                return {"status": "success", "message": f"Model updated to {new_model}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.get("/api/v1/sync/export")
        async def sync_export(since_ts: str = '2000-01-01 00:00:00'):
            try:
                from core.node_sync import NodeSynchronizer
                soul_path = getattr(self.brain, 'soul_path', 'nova_soul.db')
                sync = NodeSynchronizer(soul_path)
                data = sync.export_data(since_ts)
                return {"status": "success", "data": data}
            except Exception as e:
                import traceback
                logging.error(f"Error en /sync/export: {traceback.format_exc()}")
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/sync/import")
        async def sync_import(request: Request):
            try:
                payload = await request.json()
                from core.node_sync import NodeSynchronizer
                soul_path = getattr(self.brain, 'soul_path', 'nova_soul.db')
                sync = NodeSynchronizer(soul_path)
                result = sync.import_data(payload.get('data', {}))
                return result
            except Exception as e:
                import traceback
                logging.error(f"Error en /sync/import: {traceback.format_exc()}")
                return {"status": "error", "message": str(e)}
                
    async def start(self):
        """Start the uvicorn server in the background and open browser."""
        import os
        import webbrowser
        port = int(os.getenv("NOVA_API_PORT", 8090))
        config = uvicorn.Config(self.app, host="0.0.0.0", port=port, log_level="warning")
        server = uvicorn.Server(config)
        
        # Run server as asyncio task without failing the whole app
        async def run_server():
            # Background tasks (Node Sync)
            async def background_loop():
                import asyncio
                while True:
                    logging.info("Core maintenance: Heartbeat & Peer Sync...")
                    # Peer Sync
                    try:
                        from core.node_sync import NodeSynchronizer
                        soul_path = getattr(self.brain, 'soul_path', 'nova_soul.db')
                        sync = NodeSynchronizer(soul_path)
                        peers = sync.get_known_peers()
                        for peer in peers:
                            await sync.pull_from_peer(peer)
                    except Exception as e:
                        logging.error(f"Background Sync Error: {e}")
                    
                    await asyncio.sleep(600) # Every 10 minutes
            
            asyncio.create_task(background_loop())
            
            try:
                await server.serve()
            except BaseException as e:
                logging.error(f"API Server failed to start on port {port}: {e}")
                
        loop = asyncio.get_event_loop()
        loop.create_task(run_server())
        logging.info(f"API Server configured for port {port}.")
        
        # Auto-open browser
        dashboard_url = f"http://localhost:{port}"
        print(f"Abriendo Dashboard en: {dashboard_url}")
        webbrowser.open(dashboard_url)
