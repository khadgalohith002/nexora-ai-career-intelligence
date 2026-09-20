import subprocess
import sys
import os
import shutil

venv_dir = os.path.join(os.getcwd(), 'scratch', 'test_venv')
if os.path.exists(venv_dir):
    shutil.rmtree(venv_dir, ignore_errors=True)

print("1. Creating fresh temporary virtual environment...")
subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

venv_python = os.path.join(venv_dir, "Scripts", "python.exe")

print("2. Installing cleaned requirements.txt into temporary environment...")
subprocess.run([venv_python, "-m", "pip", "install", "--quiet", "-r", "requirements.txt"], check=True)

print("3. Verifying NEXORA app imports in clean environment...")
res = subprocess.run([venv_python, "-c", "import app; print('NEXORA LOADED SUCCESSFULLY IN CLEAN VENV!')"], capture_output=True, text=True)

print("Return code:", res.returncode)
print("Output:", res.stdout)
if res.stderr:
    print("Stderr snippet:", res.stderr[:300])

if res.returncode == 0:
    print("4. VERIFICATION SUCCESSFUL! Cleaning up temporary venv...")
    shutil.rmtree(venv_dir, ignore_errors=True)
