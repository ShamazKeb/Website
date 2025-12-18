import asyncio
from plugp100.common.credentials import AuthCredential
from plugp100.api.tapo_client import TapoClient
from plugp100.new.tapoplug import TapoPlug

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
            # 1. Credentials
            creds = AuthCredential(self.username, self.password)
            
            # 2. Client (Protocol handling)
            # v5 requires full URL? Or just IP?
            # Signature says "url: str", so we try "http://<ip>"
            client = TapoClient(creds, f"http://{ip}")
            
            # 3. Device Wrapper
            # TapoPlug(host, port, client)
            plug = TapoPlug(ip, None, client) 
            
            # 4. Update State (Connects/Auths implicitly?)
            await plug.update()
            
            # 5. Check & Toggle
            # is_on might be property or method, let's try property first
            # based on usual python patterns. If it's a method, we catch AttributeError?
            # User dir() showed 'is_on'. 
            
            # Note: plug.is_on is likely a property reading internal state populated by update()
            if plug.is_on: 
                await plug.turn_off()
                self.devices[index]["state"] = False
            else:
                await plug.turn_on()
                self.devices[index]["state"] = True
                
            return True
            
        except Exception as e:
            print(f"Error communicating with {ip}: {e}")
            return False
        finally:
            if 'client' in locals():
                await client.close()

    async def _update_state_async(self, ip, index):
        try:
            creds = AuthCredential(self.username, self.password)
            client = TapoClient(creds, f"http://{ip}")
            plug = TapoPlug(ip, None, client)
            
            await plug.update()
            
            self.devices[index]["state"] = plug.is_on
            await client.close()
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
