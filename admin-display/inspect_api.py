import plugp100.api as api_module
import inspect

print("Inspecting plugp100.api:")
for name, obj in inspect.getmembers(api_module):
    if inspect.isclass(obj):
        print(f" - Class: {name}")
