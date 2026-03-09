import aiohttp
import os
import logging

class HomeAssistantTool:
    """Native Home Assistant Integration via REST API."""
    
    def __init__(self):
        self.url = os.getenv("HA_URL", "http://homeassistant.local:8123")
        self.token = os.getenv("HA_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def check_api(self):
        """Verify API connectivity."""
        if not self.token:
            return {"status": "error", "message": "Falta HA_TOKEN en .env"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.url}/api/", headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {"status": "online", "message": data.get("message", "API OK")}
                    return {"status": "error", "message": f"HTTP {resp.status}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    async def get_states(self, entity_id=None):
        """Fetch states of all or a specific entity."""
        endpoint = f"/api/states/{entity_id}" if entity_id else "/api/states"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.url}{endpoint}", headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}

    async def call_service(self, domain, service, service_data=None):
        """Call a Home Assistant service."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.url}/api/services/{domain}/{service}"
            async with session.post(url, headers=self.headers, json=service_data or {}) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
