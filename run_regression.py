"""Quick regression + Fort Knox endpoint test."""
import subprocess, sys

result = subprocess.run(
    [r".venv-3\Scripts\python.exe", "test_safeguards.py"],
    capture_output=True, text=True, timeout=120,
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:300])
print(f"Exit code: {result.returncode}")
