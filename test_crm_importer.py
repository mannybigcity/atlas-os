import sys
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
sys.path.insert(0, str(ROOT / "skills"))

from crm_importer import crm_importer_system

def test_crm_importer_system():
    result = crm_importer_system("Test Crm Importer", {"test": True})
    assert result["system"] == "Crm Importer"
    assert result["approval_required"] is True
    assert result["status"] == "proposal_ready"
    print("Crm Importer test passed.")

if __name__ == "__main__":
    test_crm_importer_system()
