from app.core.security import verify_password, get_password_hash

def test_hashing():
    password = "secret_password"
    
    # Test 1: Hash generation
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    
    if hashed == password:
        print("FAILURE: Hash matches plain text!")
        return

    # Test 2: Verification success
    if verify_password(password, hashed):
        print("SUCCESS: Password verified correctly.")
    else:
        print("FAILURE: Password verification failed.")

    # Test 3: Verification failure
    if not verify_password("wrong_password", hashed):
        print("SUCCESS: Wrong password rejected.")
    else:
        print("FAILURE: Wrong password accepted!")

if __name__ == "__main__":
    test_hashing()
