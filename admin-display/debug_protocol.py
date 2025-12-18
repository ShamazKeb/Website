import inspect
from plugp100.protocol.tapo_protocol import TapoProtocol
# Try to find KlapProtocol
try:
    from plugp100.protocol.klap.klap_protocol import KlapProtocol
    print("✅ Found KlapProtocol")
except ImportError:
    print("❌ KlapProtocol not found")

print("\nTapoProtocol Constructor:")
print(inspect.signature(TapoProtocol.__init__))

if 'KlapProtocol' in locals():
    print("\nKlapProtocol Constructor:")
    print(inspect.signature(KlapProtocol.__init__))

# Test Instantiation
try:
    p = TapoProtocol()
    print("\n✅ TapoProtocol instantiated without args")
except Exception as e:
    print(f"\n❌ TapoProtocol instantiation failed: {e}")
