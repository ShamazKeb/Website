import asyncio
from plugp100.api.tapo_client import TapoClient
from plugp100.common.credentials import AuthCredential

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
        # Create Client
        credential = AuthCredential(self.username, self.password)
        client = TapoClient(ip, credential)
        
        try:
            # Login
            await client.login()
            
            # Get Info
            info = await client.get_device_info()
            is_on = info.to_dict()['device_on'] # Adjust based on actual response structure if needed
            
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
        finally:
            # Best practice to close session if library supports it?
            # plugp100 clients usually don't have explicit close, but let's check docs if needed.
            # Assuming it's fine for one-off.
            pass

    async def _update_state_async(self, ip, index):
        credential = AuthCredential(self.username, self.password)
        client = TapoClient(ip, credential)
        try:
            await client.login()
            info = await client.get_device_info()
            self.devices[index]["state"] = info.to_dict()['device_on']
        except:
            pass

    def toggle(self, index):
        """
        Synchronous wrapper for toggle action.
        """
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
        """
        Synchronous wrapper for updating all states.
        """
        async def main():
            tasks = []
            for i, dev in enumerate(self.devices):
                tasks.append(self._update_state_async(dev["ip"], i))
            await asyncio.gather(*tasks)
            
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"State Update Error: {e}")
