from plugp100.protocol.klap.klap_handshake_revision import KlapHandshakeRevision
import inspect

print("Inspecting KlapHandshakeRevision (V1/Base?):")
try:
    print("\nConstructor:")
    print(inspect.signature(KlapHandshakeRevision.__init__))
    
    print("\ngenerate_auth_hash:")
    print(inspect.signature(KlapHandshakeRevision.generate_auth_hash))
except Exception as e:
    print(f"Error: {e}")
