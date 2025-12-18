from tapo_manager import TapoManager
import asyncio

def test_connection():
    email = "johann@thygs.com"
    password = "SmartHome!"
    
    print(f"---Testing Tapo Connection (plugp100)---")
    print(f"User: {email}")
    
    manager = TapoManager(email, password)
    
    # We can just call update_states to test connectivity broadly
    print("\nRunning update_states()...")
    manager.update_states()
    
    print("\nDevice Status:")
    for i, dev in enumerate(manager.devices):
        state_str = "ON" if dev['state'] else "OFF"
        # If state is False it might just be default, but if update_states worked for ON devices it's good.
        # Let's try to get info explicitly for the first device to be sure.
        print(f"  {dev['name']} ({dev['ip']}): {state_str}")
        
    print("\nDone.")

if __name__ == "__main__":
    test_connection()
