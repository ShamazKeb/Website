import asyncio
from plugp100.api.tapo_client import TapoClient

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
            # v3.6.0: Client takes credentials
            client = TapoClient(self.username, self.password)
            
            # Login with IP (Library adds http:// internally)
            await client.login(ip, use_v2=True)
            
            # Get State
            result = await client.get_device_info()
            if result.is_right:
                info = result.get() # Unpack 'Either'
                # info is typically a dict in v3
                is_on = info.get('device_on', False)
                
                # Toggle
                new_state = not is_on
                await client.set_device_info({"device_on": new_state})
                
                # Update local state
                self.devices[index]["state"] = new_state
                return True
            else:
                print(f"Failed to get info for {ip}: {result}")
                return False
                
        except Exception as e:
            print(f"Error communicating with {ip}: {e}")
            return False
        finally:
            # Clean up session
            # Note: v3 TapoClient might not have close(), but underlying session does?
            # Inspect showed close() method exists.
            if client:
                await client.close()

    async def _update_state_async(self, ip, index):
        try:
            client = TapoClient(self.username, self.password)
            # Try login v2 first
            try:
                await client.login(ip, use_v2=True)
            except Exception:
                 # Fallback to v1?
                 await client.login(ip, use_v2=False)

            result = await client.get_device_info()
            if result.is_right:
                 info = result.get()
                 is_on = info.get('device_on', False)
                 self.devices[index]["state"] = bool(is_on)
            else:
                 print(f"Update failed for {ip}: {result}")
                 
        except Exception as e:
            print(f"Error updating {ip}: {e}")
            pass
        finally:
            if client:
                await client.close()

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
