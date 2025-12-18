import os
import config
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

class DisplayControl:
    def __init__(self):
        self.use_gpio = config.USE_GPIO_BACKLIGHT
        self.gpio_pin = config.BACKLIGHT_GPIO_PIN
        
        # Framebuffer Blanking Mode (New default for SPI displays)
        self.fb_path = getattr(config, 'FB_BLANK_PATH', "/sys/class/graphics/fb1/blank")
        
        if self.use_gpio and GPIO:
             try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.gpio_pin, GPIO.OUT)
                print(f"[Sheep] Initialized GPIO {self.gpio_pin} for Backlight.")
             except Exception as e:
                print(f"[Sheep] Error initializing GPIO: {e}")
                
    def _update_ipc(self, state):
        try:
            with open("/tmp/sheep_state", "w") as f:
                f.write(state)
        except Exception as e:
            print(f"[Sheep] IPC Error: {e}")

    def wake(self):
        self._update_ipc("WAKE")

    def sleep(self):
        self._update_ipc("SLEEP")
