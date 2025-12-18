from tapo_manager import TapoManager
import asyncio

def test_connection():
    email = "johann@thygs.com"
    password = "SmartHome!"
    
    print(f"---Testing Tapo Connection (plugp100 v5)---")
    print(f"User: {email}")
    
    manager = TapoManager(email, password)
    
    print("\nRunning update_states()...")
    # This runs the async update routine synchronously
    manager.update_states()
    
    print("\nDevice Status:")
    for i, dev in enumerate(manager.devices):
        state_str = "ON" if dev['state'] else "OFF"
        print(f"  {dev['name']} ({dev['ip']}): {state_str}")
        
    print("\nDone. If devices show OFF but are ON, update failed silently.")

if __name__ == "__main__":
    test_connection()
