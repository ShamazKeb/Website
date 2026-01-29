import os
import subprocess

venv_scripts = os.path.join(os.path.dirname(__file__), ".venv", "Scripts")
activate_script = os.path.join(venv_scripts, "activate_this.py")

with open(activate_script) as f:
    exec(f.read(), {'__file__': activate_script})

alembic_path = os.path.join(venv_scripts, "alembic")

result = subprocess.run(
    [
        alembic_path,
        "current",
    ],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(__file__),
)

print("--- STDOUT ---")
print(result.stdout)
print("--- STDERR ---")
print(result.stderr)
