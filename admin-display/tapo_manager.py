import asyncio
import aiohttp
from plugp100.common.credentials import AuthCredential
from plugp100.api.tapo_client import TapoClient

class TapoManager:
    def __init__(self, email, password):
        self.credential = AuthCredential(email, password)
        
        # Device Configuration
        self.devices = [
            {"name": "Dartscheibe", "ip": "192.168.178.77", "state": False},
            {"name": "Schrank", "ip": "192.168.178.32", "state": False},
            {"name": "Industrie", "ip": "192.168.178.30", "state": False},
            {"name": "Schreibtisch", "ip": "192.168.178.31", "state": False}
        ]

    async def _toggle_async(self, ip, index):
        try:
            async with aiohttp.ClientSession() as session:
                client = TapoClient.create(self.credential, ip, http_session=session)
                
                # Get current state
                result = await client.get_device_info()
                if result.is_right():
                    is_on = result.value.get('device_on', False)
                    new_state = not is_on
                    
                    # Toggle
                    await client.set_device_info({"device_on": new_state})
                    self.devices[index]["state"] = new_state
                    return True
                else:
                    print(f"[{ip}] Get Info Failed: {result}")
                    return False
                    
        except Exception:
            import traceback
            traceback.print_exc()
            return False

    async def _update_state_async(self, ip, index):
        try:
            async with aiohttp.ClientSession() as session:
                client = TapoClient.create(self.credential, ip, http_session=session)
                
                result = await client.get_device_info()
                if result.is_right():
                    is_on = result.value.get('device_on', False)
                    self.devices[index]["state"] = bool(is_on)
                else:
                    print(f"[{ip}] Update Failed: {result}")
                 
        except Exception:
            import traceback
            traceback.print_exc()

    def toggle(self, index):
        if index < 0 or index >= len(self.devices):
            return False
        device = self.devices[index]
        try:
            asyncio.run(self._toggle_async(device["ip"], index))
            return True
        except Exception as e:
            print(f"Toggle Error: {e}")
            return False

    def update_states(self):
        async def main():
            tasks = []
            for i, dev in enumerate(self.devices):
                tasks.append(self._update_state_async(dev["ip"], i))
            await asyncio.gather(*tasks)
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"State Update Error: {e}")
