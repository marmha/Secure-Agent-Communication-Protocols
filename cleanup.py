import os
import subprocess
import time

DB_FILE = "db.sqlite3"
VENV_PY = os.path.join(".venv", "Scripts", "python.exe")  # Windows path

print("=== CLEANUP START ===")

# Check if using virtual environment Python
RUN_PY = VENV_PY if os.path.exists(VENV_PY) else "python"

# 1️⃣ Remove DB file if exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Deleted:", DB_FILE)
else:
    print("DB already deleted.")

# 2️⃣ Apply migrations
print("\nRunning migrations...")
subprocess.run([RUN_PY, "manage.py", "migrate"])

# 3️⃣ Create superuser
print("\nCreating default superuser: admin / admin123")
env = os.environ.copy()
env.setdefault("DJANGO_SUPERUSER_PASSWORD", "admin123")
subprocess.run([
    RUN_PY,
    "manage.py",
    "createsuperuser",
    "--noinput",
    "--username", "admin",
    "--email", "admin@example.com"
], env=env)

print("\nSuperuser created successfully!")

# 4️⃣ Register agents automatically
print("\nRegistering agents...")
subprocess.run([RUN_PY, "register_agents.py"])

print("\n=== CLEANUP DONE 🚀 System Fresh & Ready ===")
