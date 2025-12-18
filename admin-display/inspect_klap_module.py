import plugp100.protocol.klap.klap_handshake_revision as klap_module
import inspect

print("Inspecting module plugp100.protocol.klap.klap_handshake_revision:")
for name, obj in inspect.getmembers(klap_module):
    if inspect.isclass(obj):
        print(f" - Class: {name}")
