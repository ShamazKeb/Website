import evdev
from evdev import ecodes
import threading
import time

class Touch:
    def __init__(self, dev_path='/dev/input/event0', w=320, h=480, 
                 swap_xy=False, invert_x=False, invert_y=False,
                 x_min=0, x_max=4095, y_min=0, y_max=4095):
        
        self.dev_path = dev_path
        self.device = None
        
        # Screen Dimensions
        self.w = w
        self.h = h
        
        # Calibration Config
        self.swap_xy = swap_xy
        self.invert_x = invert_x
        self.invert_y = invert_y
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        
        # State
        self.raw_x = 0
        self.raw_y = 0
        self.running = True
        
        self._connect()

    def _connect(self):
        try:
            self.device = evdev.InputDevice(self.dev_path)
            print(f"Touch device connected: {self.device.name}")
        except Exception as e:
            print(f"Touch connection error: {e}")
            self.device = None

    def _map_val(self, val, in_min, in_max, out_min, out_max):
        # Constrain
        if val < in_min: val = in_min
        if val > in_max: val = in_max
        # Map
        return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def read(self):
        """
        Polls for a touch event. Returns (x, y) (screen coords) if a touch press is detected.
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
                    self.raw_x = event.value
                elif event.code == ecodes.ABS_Y:
                    self.raw_y = event.value
            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_TOUCH and event.value == 1: # 1=Press
                    touch_triggered = True

        if touch_triggered:
            # Apply Calibration
            x_val = self.raw_x
            y_val = self.raw_y
            
            # 1. Normalize to 0.0 - 1.0 based on min/max
            # Note: Assuming linear mapping
            norm_x = (x_val - self.x_min) / (self.x_max - self.x_min)
            norm_y = (y_val - self.y_min) / (self.y_max - self.y_min)
            
            # Clamp
            norm_x = max(0.0, min(1.0, norm_x))
            norm_y = max(0.0, min(1.0, norm_y))
            
            # 2. Swap Axes
            if self.swap_xy:
                norm_x, norm_y = norm_y, norm_x
            
            # 3. Invert
            if self.invert_x:
                norm_x = 1.0 - norm_x
            if self.invert_y:
                norm_y = 1.0 - norm_y
                
            # 4. Scale to Screen
            screen_x = int(norm_x * self.w)
            screen_y = int(norm_y * self.h)
            
            return (screen_x, screen_y)
            
        return None
