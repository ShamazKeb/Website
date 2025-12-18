import asyncio
from plugp100.common.credentials import AuthCredential
from plugp100.api.tapo_client import TapoClient
from plugp100.new.tapoplug import TapoPlug
# Protocol Imports
from plugp100.protocol.klap.klap_protocol import KlapProtocol
from plugp100.protocol.klap.klap_handshake_revision import KlapHandshakeRevisionV2

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
        client = None
        try:
            # 1. Credentials
            creds = AuthCredential(self.username, self.password)
            url = f"http://{ip}"
            
            # 2. Protocol (KLAP Revision 2 is standard for new FW)
            # Use specific Revision V2 class
            protocol = KlapProtocol(creds, url, KlapHandshakeRevisionV2)
            
            # 3. Client
            client = TapoClient(creds, url, protocol)
            
            # 4. wrapper
            plug = TapoPlug(ip, None, client)
            
            # 5. Action
            await plug.update()
            
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
            if client:
                await client.close()

    async def _update_state_async(self, ip, index):
        client = None
        try:
            creds = AuthCredential(self.username, self.password)
            url = f"http://{ip}"
            protocol = KlapProtocol(creds, url, KlapHandshakeRevisionV2)
            client = TapoClient(creds, url, protocol)
            plug = TapoPlug(ip, None, client)
            
            await plug.update()
            self.devices[index]["state"] = plug.is_on
            
        except Exception as e:
            print(f"Error updating {ip}: {e}")
            pass
        finally:
            if client:
                await client.close()

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
