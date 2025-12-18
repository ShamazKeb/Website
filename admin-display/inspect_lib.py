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
    try:
        from plugp100.new.tapoplug import TapoPlug
        print("\n✅ Found TapoPlug in plugp100.new.tapoplug")
        print("Methods in TapoPlug:")
        print([m for m in dir(TapoPlug) if not m.startswith("_")])
    except ImportError:
        print("\n❌ TapoPlug NOT found in plugp100.new.tapoplug")
        
    try:
        from plugp100.api.tapo_client import TapoClient
        # Check constructor args if possible?
        print("\nTapoClient Constructor Args:")
        print(inspect.signature(TapoClient.__init__))
    except:
        pass

if __name__ == "__main__":
    inspect_lib()
