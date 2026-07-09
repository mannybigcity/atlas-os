from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))

import mason_memory


class MasonMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory_path = ROOT / "mason_workspace" / "mason_memory.json"
        if self.memory_path.exists():
            self.memory_path.unlink()

    def test_mason_remember_creates_timestamped_memory_entry(self):
        saved = mason_memory.mason_remember(
            "Mason protects Atlas focus through durable systems."
        )

        self.assertTrue(self.memory_path.exists())
        self.assertEqual(saved["entry"], "Mason protects Atlas focus through durable systems.")
        self.assertIn("timestamp", saved)

        data = json.loads(self.memory_path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(data[-1]["entry"], "Mason protects Atlas focus through durable systems.")
        self.assertEqual(data[-1]["timestamp"], saved["timestamp"])

    def test_mason_recall_returns_latest_entries_limited(self):
        mason_memory.mason_remember("first mission memory")
        mason_memory.mason_remember("second mission memory")
        mason_memory.mason_remember("third mission memory")

        recalled = mason_memory.mason_recall(limit=2)

        self.assertEqual(
            [item["entry"] for item in recalled],
            ["second mission memory", "third mission memory"],
        )
        self.assertTrue(all("timestamp" in item for item in recalled))


if __name__ == "__main__":
    unittest.main(verbosity=2)
