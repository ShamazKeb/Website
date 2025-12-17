import time
import config
from listener import Listener
from hardware import DisplayControl

class AudioWakeApp:
    def __init__(self):
        self.display = DisplayControl()
        self.listener = Listener()
        
        # State
        self.energy = config.MAX_ENERGY
        self.is_awake = True
        
        # Initialize Display On
        self.display.wake()
        print(f"[AudioWake] System started. Energy: {self.energy}")

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
        # Optional: Wake screen on exit so user isn't stuck in dark?
        # app.display.wake() 
