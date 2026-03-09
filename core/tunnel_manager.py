import asyncio
import logging
import json
import sqlite3
import websockets
from datetime import datetime

class TunnelManager:
    """Manages P2P Connections between Nova26 platforms via WebSockets."""
    
    def __init__(self, db_path, brain):
        self.db_path = db_path
        self.brain = brain
        self.active_websockets = {}  # ip_or_url -> websocket object or fastapi websocket
        self.client_task = None
        self.target_host = self._get_target_host()
        
    def _execute_query(self, query, params=(), fetch_all=True):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = True
            conn.close()
            return result
        except Exception as e:
            logging.error(f"DB Error in Tunnel: {e}")
            return []

    def _get_target_host(self):
        res = self._execute_query("SELECT value FROM config WHERE key='tunnel_target_host'")
        if res:
            return res[0]['value']
        return None

    def set_target_host(self, host_ws_url):
        self._execute_query("INSERT OR REPLACE INTO config (key, value) VALUES ('tunnel_target_host', ?)", (host_ws_url,), fetch_all=False)
        self.target_host = host_ws_url
        self.restart_client()
        
    def get_status(self):
        peers = self._execute_query("SELECT ip_address, name, role, auth_status, last_seen FROM tunnel_peers")
        return {
            "target_host": self.target_host,
            "peers": peers,
            "active_connections": list(self.active_websockets.keys())
        }

    def authorize_peer(self, ip_address):
        self._execute_query("UPDATE tunnel_peers SET auth_status='authorized' WHERE ip_address=?", (ip_address,), fetch_all=False)

    def reject_peer(self, ip_address):
        self._execute_query("UPDATE tunnel_peers SET auth_status='rejected' WHERE ip_address=?", (ip_address,), fetch_all=False)
        # We can't synchronously close FastApi WebSockets here easily unless we tracked them as such, 
        # but they will close on next poll or we can try to close if it's in our dict
        if ip_address in self.active_websockets:
            try:
                # FastApi WebSocket
                ws = self.active_websockets[ip_address]
                asyncio.create_task(ws.close())
            except:
                pass

    async def handle_incoming_connection(self, websocket, client_ip):
        """Called by FastAPI when a client tries to connect."""
        await websocket.accept()
        
        res = self._execute_query("SELECT auth_status FROM tunnel_peers WHERE ip_address=?", (client_ip,))
        auth_status = res[0]['auth_status'] if res else None
        
        if not auth_status:
            # First time seeing this IP
            self._execute_query("INSERT INTO tunnel_peers (ip_address, name, role, auth_status) VALUES (?, 'Unknown', 'client', 'pending')", (client_ip,), fetch_all=False)
            await websocket.send_text(json.dumps({"type": "auth_error", "message": "Connection pending authorization by Host."}))
            # Keep it open but effectively paused until authorized, or just close it? 
            # Usually better to close it and let them retry to see if authorized
            await websocket.close()
            return

        if auth_status != 'authorized':
            await websocket.send_text(json.dumps({"type": "auth_error", "message": f"Connection {auth_status}. Wait or contact host."}))
            await websocket.close()
            return
            
        # Authorized!
        self.active_websockets[client_ip] = websocket
        self._execute_query("UPDATE tunnel_peers SET last_seen=CURRENT_TIMESTAMP WHERE ip_address=?", (client_ip,), fetch_all=False)
        
        try:
            while True:
                raw_message = await websocket.receive_text()
                await self.process_message(client_ip, raw_message)
        except Exception:
            pass
        finally:
            if client_ip in self.active_websockets:
                del self.active_websockets[client_ip]

    async def connect_to_host(self):
        """Background task running on the Client to connect to the Host."""
        while True:
            if not self.target_host:
                await asyncio.sleep(10)
                continue
                
            try:
                res = self._execute_query("SELECT name FROM identity WHERE id=1")
                my_name = res[0]['name'] if res else "Nova26 Client"
                
                async with websockets.connect(self.target_host) as websocket:
                    await websocket.send(json.dumps({"type": "hello", "name": my_name}))
                    self.active_websockets[self.target_host] = websocket
                    try:
                        async for message in websocket:
                            await self.process_message(self.target_host, message)
                    except websockets.exceptions.ConnectionClosed:
                        pass
                    finally:
                        if self.target_host in self.active_websockets:
                            del self.active_websockets[self.target_host]
            except Exception as e:
                # Connection failed, maybe host down or we are rejected/pending
                logging.debug(f"Tunnel client waiting/retrying host {self.target_host}: {e}")
                
            await asyncio.sleep(5)

    def restart_client(self):
        if self.client_task:
            self.client_task.cancel()
        self.client_task = asyncio.create_task(self.connect_to_host())
        
    def start(self):
        """Start the background outward connection task."""
        self.restart_client()

    async def process_message(self, sender_ip, raw_message):
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type")
            
            if msg_type == "hello":
                name = data.get("name", "Unknown")
                self._execute_query("UPDATE tunnel_peers SET name=?, last_seen=CURRENT_TIMESTAMP WHERE ip_address=?", (name, sender_ip), fetch_all=False)
            elif msg_type == "agent_message":
                text = data.get("text")
                full_input = f"[Tunnel de {sender_ip}] {text}"
                await self.brain.process_input(full_input, interface='tunnel')
            
        except Exception as e:
            logging.error(f"Error processing tunnel msg from {sender_ip}: {e}")
            
    async def send_message(self, target_ip, text):
        if target_ip in self.active_websockets:
            ws = self.active_websockets[target_ip]
            payload = json.dumps({"type": "agent_message", "text": text})
            # Check if it's websockets or fastapi WebSocket
            if hasattr(ws, 'send_text'): # FastAPI
                await ws.send_text(payload)
            else: # websockets library
                await ws.send(payload)
            return True
        return False
