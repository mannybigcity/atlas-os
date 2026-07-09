import sys
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
sys.path.insert(0, str(ROOT / "skills"))

from territory_manager import territory_manager_system

def test_territory_manager_system():
    result = territory_manager_system("Test Territory Manager", {"test": True})
    assert result["system"] == "Territory Manager"
    assert result["approval_required"] is True
    assert result["status"] == "proposal_ready"
    print("Territory Manager test passed.")

if __name__ == "__main__":
    test_territory_manager_system()
