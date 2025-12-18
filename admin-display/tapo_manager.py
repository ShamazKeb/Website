from PyP100 import PyP100
import threading

class TapoManager:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
        # Device Configuration
        self.devices = [
            {"name": "Dartscheibe", "ip": "192.168.178.77", "state": False},
            {"name": "Schrank", "ip": "192.168.178.32", "state": False},
            {"name": "Industrie", "ip": "192.168.178.30", "state": False},
            {"name": "Schreibtisch", "ip": "192.168.178.31", "state": False}
        ]
        
    def _get_device(self, ip):
        p100 = PyP100.P100(ip, self.email, self.password)
        # Authentication is required for commands
        p100.handshake()
        p100.login()
        return p100

    def toggle(self, index):
        """
        Toggles the device at index. Returns success (True/False).
        Updates internal state cache.
        """
        if index < 0 or index >= len(self.devices):
            return False

        device_info = self.devices[index]
        ip = device_info["ip"]
        
        try:
            dev = self._get_device(ip)
            # Get current state first? Or just toggle based on cache?
            # To be safe, let's trying reading info, but toggle is faster if we assume cache is approx correct 
            # or just blindly set inverted.
            # PyP100 doesn't have a simple 'toggle', we need to get info.
            
            info = dev.getDeviceInfo()
            is_on = info['device_on']
            
            if is_on:
                dev.turnOff()
                self.devices[index]["state"] = False
            else:
                dev.turnOn()
                self.devices[index]["state"] = True
                
            return True
        except Exception as e:
            print(f"Error toggling {device_info['name']}: {e}")
            return False

    def update_states(self):
        """
        Background sync of states (optional, for startup)
        """
        for i, d in enumerate(self.devices):
            try:
                dev = self._get_device(d["ip"])
                info = dev.getDeviceInfo()
                self.devices[i]["state"] = info['device_on']
            except:
                pass # Offline or error
