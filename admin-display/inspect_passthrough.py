from plugp100.protocol.passthrough_protocol import PassthroughProtocol
import inspect

print("Inspecting PassthroughProtocol:")
try:
    print("\nConstructor:")
    print(inspect.signature(PassthroughProtocol.__init__))
except Exception as e:
    print(f"Error: {e}")
