"""Isolated checks for blank workspace initialization; never use real data/."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "tools" / "init_workspace.py"
VERIFICATION = WORKSPACE / ".verification"
RECORDS = {"profile.md", "progress.md", "weaknesses.md", "interviews.md", "learning-plan.md"}


class InitWorkspaceTests(unittest.TestCase):
    def setUp(self):
        VERIFICATION.mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="init-workspace-", dir=VERIFICATION))

    def tearDown(self):
        target = self.root.resolve()
        boundary = VERIFICATION.resolve()
        if target == boundary or not target.is_relative_to(boundary):
            raise RuntimeError("拒绝清理隔离验证目录以外的路径")
        shutil.rmtree(target)

    def run_init(self):
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.root)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(completed.stdout)

    def snapshot(self):
        return {
            path.name: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in (self.root / "data").iterdir()
        }

    def test_empty_workspace_has_five_blank_records(self):
        result = self.run_init()
        self.assertEqual(set(result["created"]), {f"data/{name}" for name in RECORDS})
        self.assertEqual(result["skipped"], [])
        self.assertEqual({path.name for path in (self.root / "data").iterdir()}, RECORDS)
        self.assertTrue((self.root / "exercises").is_dir())
        self.assertTrue((self.root / "projects").is_dir())
        self.assertFalse((self.root / "handoff").exists())
        documents = {name: (self.root / "data" / name).read_text(encoding="utf-8") for name in RECORDS}
        combined = "\n".join(documents.values())
        self.assertIsNone(re.search(r"\b[SAQE]-\d{4}-\d{2}-\d{2}-\d+\b|\bW-\d+\b", combined))
        self.assertIn("默认训练目标，可更正", documents["profile.md"])
        self.assertIn("不代表本次用户的新自述", documents["profile.md"])
        self.assertIn("<!-- CURRENT_STATE_START -->", documents["progress.md"])
        self.assertIn("<!-- CURRENT_STATE_END -->", documents["progress.md"])
        self.assertIn("未评估", documents["progress.md"])
        self.assertIn("空。未发生真实错误", documents["weaknesses.md"])
        self.assertIn("未发生。", documents["interviews.md"])
        self.assertIn("第1阶段，初始诊断（尚未开始）", documents["learning-plan.md"])

    def test_repeated_run_preserves_bytes_and_mtimes(self):
        self.run_init()
        before = self.snapshot()
        result = self.run_init()
        self.assertEqual(result["created"], [])
        self.assertEqual(set(result["skipped"]), {f"data/{name}" for name in RECORDS})
        self.assertEqual(self.snapshot(), before)

    def test_partial_workspace_only_fills_missing_records(self):
        (self.root / "data").mkdir()
        sentinel = self.root / "data" / "progress.md"
        sentinel.write_bytes("真实既有内容的隔离哨兵：请勿覆盖。\r\n".encode("utf-8"))
        before = (sentinel.read_bytes(), sentinel.stat().st_mtime_ns)
        result = self.run_init()
        self.assertEqual(result["skipped"], ["data/progress.md"])
        self.assertEqual(set(result["created"]), {f"data/{name}" for name in RECORDS - {"progress.md"}})
        self.assertEqual((sentinel.read_bytes(), sentinel.stat().st_mtime_ns), before)
        self.assertEqual({path.name for path in (self.root / "data").iterdir()}, RECORDS)


if __name__ == "__main__":
    unittest.main()
