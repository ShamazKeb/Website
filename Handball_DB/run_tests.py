import pytest
import os
import sys

# Ensure the project root is in the path for imports like 'app.database'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Set the DATABASE_URL environment variable for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_handball.db"

# Optional: Print some debug info
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")
print(f"DATABASE_URL env var: {os.environ.get('DATABASE_URL')}")

# Try to import aiosqlite explicitly to confirm it's available
try:
    import aiosqlite
    print("aiosqlite imported successfully in run_tests.py")
except ImportError as e:
    print(f"Failed to import aiosqlite in run_tests.py: {e}")

if __name__ == "__main__":
    # Let pytest discover tests in the current directory and subdirectories
    pytest.main(["."])
