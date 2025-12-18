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
        
        if self.use_gpio:
            if GPIO:
                try:
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(self.gpio_pin, GPIO.OUT)
                    print(f"[Sheep] Initialized GPIO {self.gpio_pin} for Backlight.")
                except Exception as e:
                    print(f"[Sheep] Error initializing GPIO: {e}")
            else:
                print("[Sheep] Error: RPi.GPIO not found but USE_GPIO_BACKLIGHT is True.")
        else:
            # Legacy File Mode
            self.path = config.BACKLIGHT_PATH
            self.available = os.path.exists(self.path) and os.access(self.path, os.W_OK)
            if not self.available:
                print(f"[Sheep] Warning: Backlight path {self.path} not writable/found.")
            
    def set_power(self, on):
        """
        True = On, False = Off
        """
        if self.use_gpio:
            if GPIO:
                # Joy-IT: High = On, Low = Off (Usually)
                state = GPIO.HIGH if on else GPIO.LOW
                try:
                    GPIO.output(self.gpio_pin, state)
                except Exception as e:
                    print(f"[Sheep] GPIO Error: {e}")
            return

        # Legacy File Mode
        if not self.available:
            return

        val = 0 if on else 1 # 0=On for standard official display
        try:
            with open(self.path, 'w') as f:
                f.write(str(val))
        except Exception as e:
            print(f"[Sheep] Error setting display: {e}")

    def wake(self):
        self.set_power(True)

    def sleep(self):
        self.set_power(False)
