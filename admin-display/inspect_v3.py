from plugp100.api.tapo_client import TapoClient
import inspect

print("Inspecting plugp100 v3.6.0 TapoClient:")
try:
    print("\nConstructor:")
    print(inspect.signature(TapoClient.__init__))
except Exception as e:
    print(f"Error inspecting constructor: {e}")

# Also check if there are other relevant classes
import plugp100
print(f"\nplugp100 version: {getattr(plugp100, '__version__', 'Unknown')}")
