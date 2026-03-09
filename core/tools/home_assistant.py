"""
Home Assistant Native Tool for Nova26
Provides abilities to interact with Home Assistant via the official REST API.
It requires HA_URL and HA_TOKEN configuration.
"""
import logging
import json
import aiohttp
from typing import Dict, Any, Optional

class HomeAssistantTool:
    def __init__(self, ha_url: str, ha_token: str):
        """
        Inicia el cliente con la URL base de Home Assistant y el Long-Lived Access Token.
        """
        self.ha_url = ha_url.rstrip("/")
        self.ha_token = ha_token
        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }
        
    async def get_state(self, entity_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de una entidad específica.
        Ejemplo: light.sala
        """
        url = f"{self.ha_url}/api/states/{entity_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return {"error": f"Entidad '{entity_id}' no encontrada."}
                    else:
                        return {"error": f"Error HTTP {response.status}: {await response.text()}"}
        except Exception as e:
            logging.error(f"Error HA get_state: {e}")
            return {"error": str(e)}

    async def call_service(self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta un servicio en Home Assistant.
        Ejemplos: 
          domain="light", service="turn_on", service_data={"entity_id": "light.sala", "brightness": 255}
          domain="script", service="good_morning", service_data={}
        """
        url = f"{self.ha_url}/api/services/{domain}/{service}"
        service_data = service_data or {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=service_data) as response:
                    if response.status == 200:
                        return await response.json() # Returns a list of state changes
                    else:
                        return {"error": f"Error HTTP {response.status}: {await response.text()}"}
        except Exception as e:
            logging.error(f"Error HA call_service: {e}")
            return {"error": str(e)}

    async def get_states(self) -> list:
        """
        Obtiene el estado de TODAS las entidades. Puede ser muy pesado; usar con cautela.
        """
        url = f"{self.ha_url}/api/states"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return [{"error": f"Error HTTP {response.status}: {await response.text()}"}]
        except Exception as e:
            logging.error(f"Error HA get_states: {e}")
            return [{"error": str(e)}]

    async def check_api(self) -> bool:
        """
        Verifica que Home Assistant esté en línea y el token sea válido.
        """
        url = f"{self.ha_url}/api/"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message") == "API running."
                    return False
        except Exception:
            return False
