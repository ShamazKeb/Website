import plugp100
import inspect
import pkgutil

def inspect_lib():
    print(f"plugp100 version: {getattr(plugp100, '__version__', 'Unknown')}")
    
    # 1. TapoClient
    try:
        from plugp100.api.tapo_client import TapoClient
        print("\n✅ Found TapoClient in plugp100.api.tapo_client")
        print("Methods in TapoClient:")
        print([m for m in dir(TapoClient) if not m.startswith("_")])
        print("\nTapoClient Constructor:")
        print(inspect.signature(TapoClient.__init__))
    except ImportError:
        print("\n❌ TapoClient NOT found")

    # 2. TapoPlug (New Structure)
    try:
        from plugp100.new.tapoplug import TapoPlug
        print("\n✅ Found TapoPlug in plugp100.new.tapoplug")
        print("Methods in TapoPlug:")
        print([m for m in dir(TapoPlug) if not m.startswith("_")])
        print("\nTapoPlug Constructor:")
        print(inspect.signature(TapoPlug.__init__))
    except ImportError as e:
        print(f"\n❌ TapoPlug NOT found in plugp100.new.tapoplug: {e}")

if __name__ == "__main__":
    inspect_lib()
