import evdev
from evdev import ecodes
import threading
import time

class Touch:
    def __init__(self, dev_path='/dev/input/event0', w=320, h=480):
        # Attempt to find the correct device if event0 is not it
        self.dev_path = dev_path
        self.device = None
        self.x, self.y = 0, 0
        self.w, self.h = w, h
        self.running = True
        self._connect()

    def _connect(self):
        try:
            self.device = evdev.InputDevice(self.dev_path)
            print(f"Touch device connected: {self.device.name}")
        except Exception as e:
            print(f"Touch connection error: {e}")
            self.device = None

    def read(self):
        """
        Polls for a touch event. Returns (x, y) if a touch release/press is detected, else None.
        This is a blocking call if used directly on device.read(), so we use a non-blocking check or loop logic in main.
        Actually, for a simple loop, we can just return the last known coordinate if a 'touch' happened.
        """
        if not self.device:
            return None

        # Drain the buffer
        try:
            events = list(self.device.read())
        except (BlockingIOError, OSError):
            return None

        touch_triggered = False
        
        for event in events:
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    # Calibration scaling
                    # XPT2046 0..4095
                    # Portrait Mode: X typically maps to Width (320)
                    self.x = int((event.value / 4095.0) * self.w) 
                elif event.code == ecodes.ABS_Y:
                    # Portrait Mode: Y typically maps to Height (480)
                    self.y = int((event.value / 4095.0) * self.h)
            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_TOUCH and event.value == 1: # 1=Press, 0=Release
                    touch_triggered = True

        if touch_triggered:
            # Simple debounce / return logic
            return (self.x, self.y)
            
        return None
