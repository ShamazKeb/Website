import asyncio
import aiohttp
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
        session = aiohttp.ClientSession()
        try:
            # v3.6.0: Pass explicit session
            client = TapoClient(self.username, self.password, session)
            
            # Login with IP
            login_result = await client.login(ip, use_v2=True)
            if not login_result.is_right:
                 login_result = await client.login(ip, use_v2=False)

            if login_result.is_right:
                # Get State
                result = await client.get_device_info()
                if result.is_right:
                    info = result.get()
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
            else:
                print(f"Login failed for {ip}: {login_result}")
                return False
                
        except Exception:
            import traceback
            traceback.print_exc()
            return False
        finally:
            await session.close()

    async def _update_state_async(self, ip, index):
        session = aiohttp.ClientSession()
        try:
            client = TapoClient(self.username, self.password, session)
            
            # Try login v2 first
            login_result = await client.login(ip, use_v2=True)
            
            if not login_result.is_right:
                # Fallback
                login_result = await client.login(ip, use_v2=False)

            if login_result.is_right:
                result = await client.get_device_info()
                if result.is_right:
                    info = result.get()
                    is_on = info.get('device_on', False)
                    self.devices[index]["state"] = bool(is_on)
                else:
                    print(f"Update failed for {ip}: {result}")
            else:
                print(f"Login failed for {ip}: {login_result}")
                 
        except Exception:
            import traceback
            traceback.print_exc()
            pass
        finally:
            await session.close()

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
