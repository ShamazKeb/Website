import time
import threading
import config
from listener import Listener
from hardware import DisplayControl

# Try importing evdev
try:
    import evdev
except ImportError:
    evdev = None

class InputMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def _monitor_loop(self):
        if not evdev:
            print("[Sheep] evdev module not found. Touch wake disabled.")
            return

        print("[Sheep] Scanning for input devices...")
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            if not devices:
                print("[Sheep] No input devices found!")
                return
                
            # Create a selector to listen to all devices
            # This is simple and effective. Any input wakes the screen.
            for dev in devices:
                print(f"[Sheep] Monitoring: {dev.name} ({dev.path})")
            
            # Simple loop reading from all
            # Ideally we use select(), but threading for each might be overkill or complex
            # Let's use a simple poller on the most likely touch device?
            # Or just asyncio. For simplicity in this script, let's pick the one with "Touch" in name
            
            touch_dev = None
            for dev in devices:
                if "Touch" in dev.name or "ADS7846" in dev.name or "Goodix" in dev.name:
                    touch_dev = dev
                    break
            
            if not touch_dev and devices:
                touch_dev = devices[0] # Fallback
            
            if touch_dev:
                print(f"[Sheep] Listening for events on {touch_dev.name}...")
                for event in touch_dev.read_loop():
                    if event.type == evdev.ecodes.EV_KEY or event.type == evdev.ecodes.EV_ABS:
                        # Any key or touch coordinate
                        self.callback()
        except Exception as e:
            print(f"[Sheep] Input Monitor Error: {e}")


class AudioWakeApp:
    def __init__(self):
        self.display = DisplayControl()
        self.listener = Listener()
        
        # Start Input Monitor
        self.input_monitor = InputMonitor(self.on_touch)
        
        # State
        self.energy = config.MAX_ENERGY
        self.is_awake = True
        
        # Initialize Display On
        self.display.wake()
        print(f"[AudioWake] System started. Energy: {self.energy}")

    def on_touch(self):
        # Callback from Input Thread
        # Refill Energy
        if not self.is_awake:
             print(f"\n[Sheep] 👆 Touch Detected! Waking up...")
             self.display.wake()
             self.is_awake = True
        
        # Reset energy to max on touch
        self.energy = config.MAX_ENERGY

    def on_audio(self, rms):
        """
        Callback from listener.
        rms: float, 0.0 to 1.0 (approx)
        """
        # --- Visualization for Calibration ---
        # Scale for visual bar (e.g. 0.0 to 0.5 range mapped to 50 chars)
        bar_len = 50
        val_clamped = min(rms, 0.5) / 0.5
        filled = int(val_clamped * bar_len)
        bar = "#" * filled + "-" * (bar_len - filled)
        
        status_icon = "🌞" if self.is_awake else "🌑"
        # formatted output: [#####-----] 0.045 | Energy: 60 | 🌞
        print(f"\r[{bar}] {rms:.4f} | E:{self.energy:02d} | {status_icon}", end="", flush=True)
        # -------------------------------------

        is_loud = rms > config.NOISE_THRESHOLD
        
        if is_loud:
            # Wake up / Recharge
            if not self.is_awake:
                # Newline to keep log clean after partial print
                print(f"\n[Sheep] 🔊 WAKE UP! (RMS: {rms:.4f})")
                self.display.wake()
                self.is_awake = True
                self.energy = config.ENERGY_PER_NOISE # Start with a buffer
            else:
                # Already awake, add energy
                self.energy += config.ENERGY_PER_NOISE
                self.energy = min(self.energy, config.MAX_ENERGY)
        else:
            # Silence -> Drain
            if self.is_awake:
                self.energy -= config.IDLE_DRAIN
                if self.energy <= 0:
                    print(f"\n[Sheep] 💤 SLEEP (Silence timeout)")
                    self.display.sleep()
                    self.is_awake = False
                    self.energy = 0

    def run(self):
        # Start listening loop
        # This blocks, so it essentially becomes the main loop
        self.listener.listen_loop(self.on_audio)

if __name__ == "__main__":
    app = AudioWakeApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[AudioWake] Exiting...")
        try:
            # Cleanup GPIO
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        except:
            pass
 
