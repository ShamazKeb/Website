import requests
import json
from app.models.player import Hand, Position

# Use verify_schema_updates.py to test the changes against the running server OR usage of the underlying function (if we want unit test)
# But since server is running, let's use requests or just mocked manual test logic if I can't hit the server easily from here (port 8000).
# Actually, I can use the client from tests.

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_create_full_player():
    # 1. Get Admin Token (simulated)
    # We need a token. Let's create one manually.
    token = create_access_token(data={"sub": "admin@test.com"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Payload with ALL fields
    payload = {
        "email": "full_player@test.com",
        "password": "password123",
        "first_name": "Full",
        "last_name": "Player",
        "year_of_birth": 1999,
        "hand": "LINKS",
        "position": "RL",
        "jersey_number": 10,
        "height_cm": 185,
        "weight_kg": 85.5,
        "notes": "Test notes"
    }
    
    # 3. Request
    # Note: We need to ensure we don't conflict with existing user.
    # The setup script might have reset DB, but let's use a unique email.
    
    try:
        response = client.post("/admin/players", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Player created with full schema.")
            print(json.dumps(data, indent=2))
            
            # Verify fields
            assert data["hand"] == "LINKS"
            assert data["position"] == "RL"
            assert data["jersey_number"] == 10
            assert data["notes"] == "Test notes"
            print("✅ All fields verified in response.")
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_create_full_player()
