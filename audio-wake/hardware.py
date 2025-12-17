import os
import config

class DisplayControl:
    def __init__(self):
        self.path = config.BACKLIGHT_PATH
        self.available = os.path.exists(self.path) and os.access(self.path, os.W_OK)
        if not self.available:
            print(f"[Sheep] Warning: Backlight path {self.path} not writable/found.")
            
    def set_power(self, on):
        """
        True = On, False = Off
        """
        if not self.available:
            return

        val = config.DISPLAY_ON if on else config.DISPLAY_OFF
        try:
            with open(self.path, 'w') as f:
                f.write(str(val))
        except Exception as e:
            print(f"[Sheep] Error setting display: {e}")

    def wake(self):
        self.set_power(True)

    def sleep(self):
        self.set_power(False)
