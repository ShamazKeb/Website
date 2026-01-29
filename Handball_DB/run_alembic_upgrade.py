import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

venv_scripts = os.path.join(os.path.dirname(__file__), ".venv", "Scripts")
alembic_path = os.path.join(venv_scripts, "alembic")

# Ensure the database file exists if it's SQLite
db_url = os.getenv("DATABASE_URL")
if db_url and "sqlite" in db_url:
    db_file = db_url.split("///")[-1]
    if not os.path.exists(db_file):
        # Create an empty file if it doesn't exist
        open(db_file, 'a').close()
        print(f"Created empty database file: {db_file}")

command = ["python", "-m", "alembic", "upgrade", "head"]
print(f"Running command: {' '.join(command)}")

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    cwd=os.path.dirname(__file__),
    env=os.environ.copy() # Pass current environment variables
)

print("--- STDOUT ---")
print(result.stdout)
print("--- STDERR ---")
print(result.stderr)

if result.returncode != 0:
    print(f"Alembic upgrade failed with exit code {result.returncode}")
else:
    print("Alembic upgrade successful.")
