import plugp100
import inspect
import pkgutil

def inspect_lib():
    print(f"plugp100 version: {getattr(plugp100, '__version__', 'Unknown')}")
    print(f"Path: {plugp100.__path__}")
    
    # Walk through packages
    for importer, modname, ispkg in pkgutil.walk_packages(plugp100.__path__, prefix="plugp100."):
        print(f"Found module: {modname}")
        
    # Try to find TapoClient and TapoPlug
    try:
        from plugp100.api.tapo_client import TapoClient
        print("\n✅ Found TapoClient in plugp100.api.tapo_client")
        print("Methods in TapoClient:")
        print([m for m in dir(TapoClient) if not m.startswith("_")])
    except ImportError:
        print("\n❌ TapoClient NOT found in plugp100.api.tapo_client")

    try:
        from plugp100.api.tapo_plug import TapoPlug
        print("\n✅ Found TapoPlug in plugp100.api.tapo_plug")
    except ImportError:
        print("\n❌ TapoPlug NOT found in plugp100.api.tapo_plug")

    try:
        from plugp100.domain.smart_plug import SmartPlug
        print("\n✅ Found SmartPlug in plugp100.domain.smart_plug")
    except ImportError:
        print("\n❌ SmartPlug NOT found in plugp100.domain.smart_plug")

if __name__ == "__main__":
    inspect_lib()
