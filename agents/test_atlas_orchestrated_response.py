from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.atlas_orchestrated_response import atlas_orchestrated_response

tests = [
    "Build a CRM",
    "Find revenue opportunities",
    "Improve the website",
    "Fix Atlas memory",
]

for t in tests:
    result = atlas_orchestrated_response(t)
    assert result["status"] == "success"
    assert result["mode"] == "orchestrated"
    print(t, "=> PASS")

print("ATLAS ORCHESTRATED RESPONSE GATEWAY VERIFIED")
