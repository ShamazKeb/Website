import plugp100.new.device_factory as factory_module
import inspect

print("Inspecting plugp100.new.device_factory module:")
for name, obj in inspect.getmembers(factory_module):
    if inspect.isclass(obj):
        print(f" - Class: {name}")
