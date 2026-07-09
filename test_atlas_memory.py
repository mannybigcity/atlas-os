from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory import memory as puter_memory


class AtlasMemoryTests(unittest.TestCase):
    def test_memory_file_is_absolute_and_survives_non_project_cwd(self):
        original_cwd = Path.cwd()
        expected_count = len(puter_memory.load_memory())
        try:
            os.chdir(Path.home())
            self.assertTrue(puter_memory.MEMORY_FILE.is_absolute())
            self.assertEqual(puter_memory.MEMORY_FILE, ROOT / "memory" / "memory.json")
            self.assertEqual(len(puter_memory.load_memory()), expected_count)
        finally:
            os.chdir(original_cwd)

    def test_save_fact_uses_configurable_absolute_memory_file(self):
        original_memory_file = puter_memory.MEMORY_FILE
        test_memory_file = ROOT / "mason_workspace" / f"atlas_memory_test_{os.getpid()}.json"
        test_fact = "Atlas memory writes survive cwd changes."
        try:
            puter_memory.MEMORY_FILE = test_memory_file.resolve()
            before = len(puter_memory.load_memory())
            os.chdir(Path.home())
            puter_memory.save_fact(test_fact)

            saved = json.loads(test_memory_file.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(saved), before + 1)
            self.assertEqual(saved[-1], test_fact)
        finally:
            puter_memory.MEMORY_FILE = original_memory_file
            os.chdir(ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
