from tapo_manager import TapoManager
import time

def test_connection():
    email = "johann@thygs.com"
    password = "SmartHome!"
    
    print(f"---Testing Tapo Connection---")
    print(f"User: {email}")
    
    manager = TapoManager(email, password)
    
    print(f"\nFound {len(manager.devices)} configured devices.")
    
    for i, dev in enumerate(manager.devices):
        print(f"\nTesting Device {i+1}: {dev['name']} ({dev['ip']})")
        try:
            print("  Connecting...")
            # We bypass the manager's cached state and try direct p100 access
            p100 = manager._get_device(dev['ip'])
            
            print("  Getting Info...")
            info = p100.getDeviceInfo()
            
            is_on = info['device_on']
            print(f"  ✅ SUCCESS! State: {'ON' if is_on else 'OFF'}")
            print(f"  Device ID: {info.get('device_id', 'Unknown')}")
            
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            print("  (Check IP, Password, or if Device is reachable)")

if __name__ == "__main__":
    test_connection()
