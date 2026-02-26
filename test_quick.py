"""Quick test of just the boring-validate endpoint with docstrings."""
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

# Code with a docstring
code = 'def process(x: int) -> bool:\n    """Check value."""\n    return x > 5\n'

body = {"code": code}
data = json.dumps(body).encode()
req = urllib.request.Request(
    f"{BASE}/safeguards/boring-validate",
    data=data,
    headers={"Content-Type": "application/json"},
)

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    print("Status: OK")
    print("Result:", json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
