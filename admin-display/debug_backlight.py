import RPi.GPIO as GPIO
import time

PINS = [18, 12, 27, 22]

def test_pin(pin):
    print(f"Testing GPIO {pin}...")
    try:
        GPIO.setup(pin, GPIO.OUT)
        
        print(f"  -> GPIO {pin} LOW (OFF?)")
        GPIO.output(pin, GPIO.LOW)
        time.sleep(2)
        
        print(f"  -> GPIO {pin} HIGH (ON?)")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(2)
        
        # Cleanup this pin to input to be safe? 
        # Or leave it high?
        GPIO.output(pin, GPIO.HIGH)
        
    except Exception as e:
        print(f"  Error on {pin}: {e}")

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    print("=== Backlight Debug Tool ===")
    print("This script will toggle common backlight pins.")
    print("Please watch the display.")
    
    for pin in PINS:
        test_pin(pin)
        
    print("Done. Cleaning up (Pins set to HIGH/Input)")
    GPIO.cleanup()

if __name__ == "__main__":
    main()
