import asyncio
from plugp100.api.tapo_client import TapoClient
# In v3.6.1, it's typically just TapoClient handling everything for plugs

class TapoManager:
    def __init__(self, email, password):
        self.username = email
        self.password = password
        
        # Device Configuration
        self.devices = [
            {"name": "Dartscheibe", "ip": "192.168.178.77", "state": False},
            {"name": "Schrank", "ip": "192.168.178.32", "state": False},
            {"name": "Industrie", "ip": "192.168.178.30", "state": False},
            {"name": "Schreibtisch", "ip": "192.168.178.31", "state": False}
        ]

    async def _toggle_async(self, ip, index):
        try:
            # v3 API: Client is directly instantiated with creds
            client = TapoClient(ip, self.username, self.password)
            
            # Login
            await client.login()
            
            # Get State (get_device_info returns an object/dict)
            info = await client.get_device_info()
            # Note: In older versions this might return a dict directly or an object with .to_dict()
            # We'll assume object and try-access or use .to_dict() if needed. 
            # Usually .device_on property or dict key 'device_on'
            
            # Let's inspect briefly via trial/error or assuming dict access on the object property
            # Actually, most v3 examples show `info.device_on`
            
            is_on = getattr(info, 'device_on', None)
            if is_on is None:
                # Fallback if it's a dict
                is_on = info.get('device_on', False)

            if is_on:
                await client.turn_off()
                self.devices[index]["state"] = False
            else:
                await client.turn_on()
                self.devices[index]["state"] = True
                
            return True
        except Exception as e:
            print(f"Error communicating with {ip}: {e}")
            return False

    async def _update_state_async(self, ip, index):
        try:
            client = TapoClient(ip, self.username, self.password)
            await client.login()
            info = await client.get_device_info()
            
            # Logic to extract state
            is_on = getattr(info, 'device_on', None)
            if is_on is None and hasattr(info, 'to_dict'):
                 is_on = info.to_dict().get('device_on')
            if is_on is None and isinstance(info, dict):
                 is_on = info.get('device_on')
            
            self.devices[index]["state"] = bool(is_on)
            
        except Exception as e:
            print(f"Error updating {ip}: {e}")
            pass

    def toggle(self, index):
        if index < 0 or index >= len(self.devices):
            return False
        device = self.devices[index]
        try:
            asyncio.run(self._toggle_async(device["ip"], index))
            return True
        except Exception as e:
            print(f"Sync Toggle Error: {e}")
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
