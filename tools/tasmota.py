import aiohttp
import logging

class TasmotaTool:
    """Direct Tasmota Interaction via HTTP API."""
    
    def __init__(self):
        # Tasmota doesn't need a central URL, we use IPs directly or Hostnames
        pass

    async def send_command(self, ip, cmnd):
        """Send a generic Tasmota command."""
        async with aiohttp.ClientSession() as session:
            # Format: http://<ip>/cm?cmnd=<cmnd>
            url = f"http://{ip}/cm?cmnd={cmnd}"
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"error": f"HTTP {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    async def rf_send(self, ip, rf_code):
        """Send a 433MHz code via Sonoff RF Bridge."""
        # Tasmota RF Bridge uses RfCode command
        # Syntax: RfCode #<hexcode>
        return await self.send_command(ip, f"RfCode {rf_code}")

    async def toggle(self, ip, power_index=1):
        """Toggle power states."""
        return await self.send_command(ip, f"Power{power_index} toggle")

    async def set_power(self, ip, state="on", power_index=1):
        """Set power to ON or OFF."""
        val = 1 if state.lower() == "on" else 0
        return await self.send_command(ip, f"Power{power_index} {val}")
