"""Quick test of the full-analysis endpoint."""
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8000"

code = 'import json\ndef process(x: int) -> bool:\n    """Check value."""\n    return x > 5\n'

body = {"code": code, "layer": "domain"}
data = json.dumps(body).encode()
req = urllib.request.Request(
    f"{BASE}/safeguards/full-analysis",
    data=data,
    headers={"Content-Type": "application/json"},
)

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    print("Status: OK")
    print("all_safeguards_pass:", result["all_safeguards_pass"])
    print("summary:", result["summary"])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Body: {e.read().decode()[:500]}")
except Exception as e:
    print(f"Error: {e}")
