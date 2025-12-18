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
                
    def set_power(self, on):
        """
        True = On, False = Off
        """
        # 1. Try GPIO (if enabled)
        if self.use_gpio and GPIO:
            state = GPIO.HIGH if on else GPIO.LOW
            try:
                GPIO.output(self.gpio_pin, state)
            except Exception as e:
                print(f"[Sheep] GPIO Error: {e}")
            return
            
        # 2. Try Framebuffer Blanking (fb1 usually)
        # 0 = Unblank (On), 1 = Blank (Off) - Standard Kernel FB
        val = 0 if on else 1
        
        # Try writing to FB path
        try:
            if os.path.exists(self.fb_path):
                with open(self.fb_path, 'w') as f:
                    f.write(str(val))
            else:
                # Fallback to fb0?
                fallback = "/sys/class/graphics/fb0/blank"
                if os.path.exists(fallback):
                     with open(fallback, 'w') as f:
                        f.write(str(val))
        except Exception as e:
            print(f"[Sheep] Error setting FB blank: {e}")

    def wake(self):
        self.set_power(True)

    def sleep(self):
        self.set_power(False)
