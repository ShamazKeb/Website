import asyncio
import aiohttp
from plugp100.common.credentials import AuthCredential
from plugp100.api.tapo_client import TapoClient
from plugp100.api.plug_device import PlugDevice

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
                plug = PlugDevice(client)
                
                # Get current state
                result = await plug.get_state()
                if hasattr(result, 'value'):
                    is_on = result.value.device_on
                    
                    # Toggle using on/off methods
                    if is_on:
                        await plug.off()
                        self.devices[index]["state"] = False
                    else:
                        await plug.on()
                        self.devices[index]["state"] = True
                    return True
                else:
                    print(f"[{ip}] Get State Failed: {result}")
                    return False
                    
        except Exception:
            import traceback
            traceback.print_exc()
            return False

    async def _update_state_async(self, ip, index):
        try:
            async with aiohttp.ClientSession() as session:
                client = TapoClient.create(self.credential, ip, http_session=session)
                plug = PlugDevice(client)
                
                result = await plug.get_state()
                if hasattr(result, 'value'):
                    self.devices[index]["state"] = result.value.device_on
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
