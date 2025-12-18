from plugp100.api.tapo_client import TapoClient
import inspect
import pkgutil
import plugp100

print("Inspecting TapoClient methods:")
for name, func in inspect.getmembers(TapoClient, predicate=inspect.isfunction):
    if not name.startswith("_"):
        print(f" - {name}{inspect.signature(func)}")

print("\nChecking for plugp100.api.smart_plug:")
try:
    from plugp100.api import smart_plug
    print(" - Found plugp100.api.smart_plug")
    print("Classes in smart_plug:")
    for name, obj in inspect.getmembers(smart_plug, predicate=inspect.isclass):
        print(f"   - {name}")
except ImportError:
    print(" - plugp100.api.smart_plug NOT found")

print("\nChecking for plugp100.api.tapo_plug:")
try:
    from plugp100.api import tapo_plug
    print(" - Found plugp100.api.tapo_plug")
except ImportError:
    print(" - plugp100.api.tapo_plug NOT found")
