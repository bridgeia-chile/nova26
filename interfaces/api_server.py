"""
API Server
A minimalistic local FastAPI server to allow external tools to send webhooks or interact.
"""
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
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
                    
                    # Fetch recent security events
                    cursor.execute("SELECT event_type, severity, details, timestamp FROM security_events ORDER BY timestamp DESC LIMIT 5")
                    security_events = [
                        {"type": r[0], "severity": r[1], "details": r[2], "timestamp": r[3]}
                        for r in cursor.fetchall()
                    ]
                    conn.close()
                except Exception as e:
                    logging.error(f"Error calculating Stitch usage or fetching security events: {e}")
                    security_events = []

                return {
                    "agents": sorted_agents,
                    "db_size": f"{db_size_kb:.1f} KB" if db_size_kb < 1024 else f"{(db_size_kb/1024):.1f} MB",
                    "sessions_count": len(getattr(self.brain, 'active_sessions', [])),
                    "system_metrics": system_metrics,
                    "update_available": getattr(self.brain, 'update_available', False),
                    "stitch_usage_monthly": stitch_usage_monthly,
                    "security_events": security_events
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
                # Retorna solo modelos habilitados
                async with self.brain.db.conn.execute("SELECT id FROM models_config WHERE is_enabled = 1") as cursor:
                    models = [row[0] for row in await cursor.fetchall()]
                
                # Si la tabla está vacía (no debería), usamos fallback
                if not models:
                    models = ["Llama-3.3-70b", "gpt-4o", "gemini-pro"]
                    
                return {"status": "success", "models": models}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.get("/api/v1/settings/models")
        async def get_all_models_config():
            try:
                async with self.brain.db.conn.execute("SELECT * FROM models_config") as cursor:
                    rows = await cursor.fetchall()
                    models = [dict(r) for r in rows]
                return {"status": "success", "models": models}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/settings/models/{model_id}")
        async def update_model_config(model_id: str, request: Request):
            try:
                data = await request.json()
                temp = data.get("temperature")
                enabled = data.get("is_enabled")
                
                if temp is not None:
                    await self.brain.db.conn.execute(
                        "UPDATE models_config SET temperature = ? WHERE id = ?", (temp, model_id)
                    )
                if enabled is not None:
                    await self.brain.db.conn.execute(
                        "UPDATE models_config SET is_enabled = ? WHERE id = ?", (1 if enabled else 0, model_id)
                    )
                
                await self.brain.db.conn.commit()
                return {"status": "success", "message": f"Configuración de {model_id} actualizada."}
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

        @self.app.websocket("/ws/tunnel")
        async def websocket_tunnel(websocket: WebSocket):
            client_ip = websocket.client.host
            await self.brain.tunnel.handle_incoming_connection(websocket, client_ip)

        @self.app.post("/api/v1/tunnel/authorize")
        async def tunnel_authorize(request: Request):
            try:
                data = await request.json()
                ip_address = data.get("ip_address")
                action = data.get("action")
                if action == "authorize":
                    self.brain.tunnel.authorize_peer(ip_address)
                elif action == "reject":
                    self.brain.tunnel.reject_peer(ip_address)
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/tunnel/host")
        async def tunnel_host(request: Request):
            try:
                data = await request.json()
                host_ws_url = data.get("host_url")
                self.brain.tunnel.set_target_host(host_ws_url)
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.get("/api/v1/tunnel/status")
        async def tunnel_status():
            try:
                return {"status": "success", "data": self.brain.tunnel.get_status()}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.get("/api/v1/config/ha")
        async def config_ha_get():
            try:
                import os
                url = os.getenv("HA_URL", "")
                token = "**********" if os.getenv("HA_TOKEN") else ""
                return {"status": "success", "ha_url": url, "ha_token_set": bool(token)}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        @self.app.post("/api/v1/config/ha")
        async def config_ha_post(request: Request):
            try:
                data = await request.json()
                ha_url = data.get("ha_url", "")
                ha_token = data.get("ha_token", "")
                
                import os
                from pathlib import Path
                # Save to .env logic simply for persistence
                env_path = Path(".env")
                env_dict = {}
                if env_path.exists():
                    with open(env_path, "r") as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                k, v = line.strip().split('=', 1)
                                env_dict[k] = v
                
                if ha_url:
                    env_dict["HA_URL"] = ha_url
                    os.environ["HA_URL"] = ha_url
                if ha_token and ha_token != "**********":
                    env_dict["HA_TOKEN"] = ha_token
                    os.environ["HA_TOKEN"] = ha_token
                
                with open(env_path, "w") as f:
                    for k, v in env_dict.items():
                        f.write(f"{k}={v}\n")
                        
                return {"status": "success"}
            except Exception as e:
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
