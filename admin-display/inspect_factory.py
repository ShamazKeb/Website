from plugp100.new.device_factory import DeviceFactory
import inspect

print("Inspecting DeviceFactory:")
try:
    print("Methods:")
    print([m for m in dir(DeviceFactory) if not m.startswith("_")])
    
    if hasattr(DeviceFactory, 'create'):
        print("\ncreate signature:")
        print(inspect.signature(DeviceFactory.create))
        
    if hasattr(DeviceFactory, 'login'):
        print("\nlogin signature:")
        print(inspect.signature(DeviceFactory.login))
except Exception as e:
    print(f"Error inspecting factory: {e}")
