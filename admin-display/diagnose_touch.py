import evdev
from evdev import ecodes
import sys

def main():
    print("Looking for touch device...")
    dev_path = '/dev/input/event0' # Default
    
    # Try to verify device
    try:
        device = evdev.InputDevice(dev_path)
        print(f"Connected to: {device.name}")
    except Exception as e:
        print(f"Failed to connect to {dev_path}: {e}")
        return

    print("------------------------------------------------")
    print("Please touch the screen at the following points:")
    print("1. TOP-LEFT")
    print("2. BOTTOM-RIGHT")
    print("------------------------------------------------")
    print("Press CTRL+C to exit.")
    
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    print(f"ABS_X: {event.value}")
                elif event.code == ecodes.ABS_Y:
                    print(f"ABS_Y: {event.value}")
            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_TOUCH:
                    print(f"TOUCH: {'DOWN' if event.value == 1 else 'UP'}")
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()
