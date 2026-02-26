"""Run test_safeguards.py and write output to test_results_final.txt."""
import subprocess
import sys

result = subprocess.run(
    [r".venv-3\Scripts\python.exe", "test_safeguards.py"],
    capture_output=True, text=True, timeout=120,
)
with open("test_results_final.txt", "w") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
    f.write(f"\nExit code: {result.returncode}\n")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
print(f"Exit code: {result.returncode}")
