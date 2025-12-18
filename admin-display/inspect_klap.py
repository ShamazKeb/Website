from plugp100.protocol.klap.klap_handshake_revision import KlapHandshakeRevision
import inspect

print("Inspecting KlapHandshakeRevision:")
# List all public attributes
attributes = [m for m in dir(KlapHandshakeRevision) if not m.startswith("_")]
print(f"Attributes: {attributes}")

# Check value of attributes if they look like revisions
for attr in attributes:
    val = getattr(KlapHandshakeRevision, attr)
    print(f" - {attr}: {val} (Type: {type(val)})")
