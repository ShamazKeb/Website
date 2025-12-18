from plugp100.protocol.klap.klap_handshake_revision import KlapHandshakeRevisionV2
import inspect

print("Inspecting KlapHandshakeRevisionV2:")
try:
    print("\nConstructor:")
    print(inspect.signature(KlapHandshakeRevisionV2.__init__))
except:
    print("No __init__ found or inspect failed.")

try:
    print("\ngenerate_auth_hash:")
    print(inspect.signature(KlapHandshakeRevisionV2.generate_auth_hash))
except:
    print("generate_auth_hash not found.")
