"""Exercise the public distribution CLI entirely in disposable workspace copies.

Run with ``python -B -m unittest discover -s verification -p test_distribution.py``.
Only canonical public skill resources are copied; no real student data is read.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit
import zipfile


WORKSPACE = Path(__file__).resolve().parents[1]
BUILDER = WORKSPACE / "tools/build_distribution.py"
CANONICAL = ".agents/skills/career-mentor"
PLUGIN = "plugins/career-mentor"
MARKETPLACE = ".agents/plugins/marketplace.json"
ARCHIVE = "dist/career-mentor-skills-only.zip"
CHECKSUM = "dist/career-mentor-skills-only.sha256"
REFERENCES = ("core", "training", "interviews", "records", "roadmap", "handoff")
PUBLIC_SKILL_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    *(f"references/{name}.md" for name in REFERENCES),
    "assets/record-templates.md",
    "assets/report-template.md",
    "assets/chatgpt-adapter.md",
    "scripts/review_schedule.py",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]+\]\(([^)\s]+)(?:\s+\"[^\"\n]*\")?\)")


class DistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.isolation = (WORKSPACE / ".verification").resolve()
        self.isolation.mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="distribution-test-", dir=self.isolation))
        self.addCleanup(self.remove_isolated_copy)
        shutil.copytree(
            WORKSPACE / CANONICAL,
            self.root / CANONICAL,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )

    def remove_isolated_copy(self) -> None:
        # Check the resolved deletion target before any recursive cleanup.
        target = self.root.resolve()
        self.assertNotEqual(target, self.isolation)
        self.assertTrue(target.is_relative_to(self.isolation))
        self.assertTrue(target.name.startswith("distribution-test-"))
        shutil.rmtree(target)

    def run_builder(self, *options: str, expected: int = 0) -> dict:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--root", str(self.root), *options],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            expected,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        payload = result.stdout if expected in (0, 1) else result.stderr
        return json.loads(payload)

    def write(self, relative: str, content: bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def source_text(self, relative: str) -> str:
        return (self.root / CANONICAL / relative).read_text(encoding="utf-8-sig").rstrip()

    def snapshot(self) -> dict:
        """Include modification times to detect rewriting even identical bytes."""
        result = {}
        for path in [self.root, *sorted(self.root.rglob("*"))]:
            relative = path.relative_to(self.root).as_posix()
            result[relative] = (
                path.is_dir(),
                path.stat().st_mtime_ns,
                None if path.is_dir() else path.read_bytes(),
            )
        return result

    def test_generated_teaching_materials_match_canonical_sources(self) -> None:
        summary = self.run_builder()
        instructions_bytes = (self.root / "CHATGPT_INSTRUCTIONS.md").read_bytes()
        instructions = instructions_bytes.decode("utf-8")
        self.assertLess(len(instructions), 8000)
        self.assertEqual(summary["instructions_chars"], len(instructions))
        start = "<!-- CORE_STANDARD_START -->\n\n"
        end = "\n\n<!-- CORE_STANDARD_END -->"
        self.assertEqual(instructions.count(start), 1)
        self.assertEqual(instructions.count(end), 1)
        embedded_core = instructions.split(start, 1)[1].split(end, 1)[0]
        self.assertEqual(embedded_core, self.source_text("references/core.md"))
        self.assertTrue(instructions.endswith(self.source_text("assets/report-template.md") + "\n"))
        for relative in (
            "handoff/chatgpt-project-instructions.md",
            f"{PLUGIN}/assets/CHATGPT_INSTRUCTIONS.md",
        ):
            with self.subTest(instructions=relative):
                self.assertEqual((self.root / relative).read_bytes(), instructions_bytes)
        for generated, canonical in (
            ("templates/LEARNING_RECORD_TEMPLATE.md", "assets/record-templates.md"),
            ("templates/TRAINING_REPORT_TEMPLATE.md", "assets/report-template.md"),
        ):
            with self.subTest(template=generated):
                self.assertEqual(
                    (self.root / generated).read_bytes(),
                    (self.root / CANONICAL / canonical).read_bytes(),
                )
        for name in REFERENCES:
            with self.subTest(standard=name):
                generated = (self.root / f"standards/{name}.md").read_text(encoding="utf-8")
                body = generated.split("\n\n", 1)[1].rstrip()
                expected = self.source_text(f"references/{name}.md")
                expected = expected.replace("../assets/report-template.md", "../templates/TRAINING_REPORT_TEMPLATE.md")
                expected = expected.replace("../assets/record-templates.md", "../templates/LEARNING_RECORD_TEMPLATE.md")
                self.assertEqual(body, expected)

    def test_zip_is_public_skills_only_and_all_resource_links_resolve(self) -> None:
        marker = b"PRIVATE-DISTRIBUTION-TEST-MARKER-DO-NOT-PACK"
        private_paths = (
            "data/profile.md", "exercises/private.py", "projects/private.md",
            "handoff/latest-report.md", "handoff/imports/private.md", ".env",
            "secrets/private.txt", "mcp.json", "apps.json", "hooks/private.py",
        )
        for relative in private_paths:
            self.write(relative, marker)
        self.run_builder()
        expected_members = {
            "plugin.json", ".codex-plugin/plugin.json",
            "assets/CHATGPT_INSTRUCTIONS.md", "assets/CHATGPT_REFERENCE.md",
            *(f"skills/career-mentor/{name}" for name in PUBLIC_SKILL_FILES),
        }
        with zipfile.ZipFile(self.root / ARCHIVE) as archive:
            members = set(archive.namelist())
            self.assertEqual(members, expected_members)
            self.assertEqual(len(archive.namelist()), len(members), "duplicate ZIP paths")
            for member in members:
                with self.subTest(member=member):
                    path = PurePosixPath(member)
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    self.assertNotIn("\\", member)
                    self.assertNotIn(":", member)
                    self.assertNotIn(marker, archive.read(member))
            portable = json.loads(archive.read("plugin.json"))
            compatibility = json.loads(archive.read(".codex-plugin/plugin.json"))
            for field in ("name", "version", "description", "author"):
                self.assertEqual(portable[field], compatibility[field])
            self.assertEqual(portable["name"], "career-mentor")
            interface = portable["extensions"]["com.openai"]["interface"]
            self.assertIsInstance(interface, dict)
            prompts = interface["defaultPrompt"]
            self.assertIsInstance(prompts, list)
            self.assertTrue(prompts)
            self.assertTrue(all(isinstance(value, str) and value for value in prompts))
            self.assertEqual(interface, compatibility["interface"])
            skills_prefix = compatibility["skills"].removeprefix("./").rstrip("/") + "/"
            self.assertTrue(any(member.startswith(skills_prefix) for member in members))
            for manifest in (portable, compatibility):
                self.assertFalse({"mcpServers", "mcp", "apps", "hooks"} & manifest.keys())
            checked_links = 0
            for member in members:
                if not member.endswith(".md"):
                    continue
                for match in MARKDOWN_LINK.finditer(archive.read(member).decode("utf-8-sig")):
                    target = match.group(1)
                    parsed = urlsplit(target)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(member), parsed.path))
                    with self.subTest(link_from=member, target=target):
                        self.assertIn(resolved, members)
                    checked_links += 1
            self.assertGreater(checked_links, 0)
        for relative in private_paths:
            self.assertEqual((self.root / relative).read_bytes(), marker)

    def test_repeated_builds_produce_identical_zip_and_sha256(self) -> None:
        first = self.run_builder()
        archive_bytes = (self.root / ARCHIVE).read_bytes()
        checksum_bytes = (self.root / CHECKSUM).read_bytes()
        digest = hashlib.sha256(archive_bytes).hexdigest()
        self.assertEqual(first["sha256"], digest)
        self.assertEqual(checksum_bytes, f"{digest}  {PurePosixPath(ARCHIVE).name}\n".encode("ascii"))
        second = self.run_builder()
        self.assertEqual(second["changed"], 0)
        self.assertEqual(second["sha256"], digest)
        self.assertEqual((self.root / ARCHIVE).read_bytes(), archive_bytes)
        self.assertEqual((self.root / CHECKSUM).read_bytes(), checksum_bytes)

    def test_check_never_writes_and_rebuild_repairs_changed_output(self) -> None:
        before = self.snapshot()
        missing = self.run_builder("--check", expected=1)
        self.assertEqual(missing["status"], "outdated")
        self.assertEqual(self.snapshot(), before)
        self.run_builder()
        before = self.snapshot()
        self.assertEqual(self.run_builder("--check")["status"], "ok")
        self.assertEqual(self.snapshot(), before)
        output = self.root / "CHATGPT_INSTRUCTIONS.md"
        original = output.read_bytes()
        output.write_bytes(original + b"\nLOCAL-EDIT-TEST\n")
        before = self.snapshot()
        stale = self.run_builder("--check", expected=1)
        self.assertIn("CHATGPT_INSTRUCTIONS.md", stale["changed"])
        self.assertEqual(self.snapshot(), before)
        self.run_builder()
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(self.run_builder("--check")["status"], "ok")

    def test_marketplace_merge_preserves_unrelated_metadata_and_entries(self) -> None:
        other = {"name": "other-plugin", "source": {"source": "local", "path": "./plugins/other"}, "custom": [1, 2]}
        initial = {
            "name": "my-existing-marketplace", "displayName": "保留顶层显示名",
            "interface": {"displayName": "保留界面显示名", "custom": True},
            "custom": {"owner": "local"}, "plugins": [other],
        }
        self.write(MARKETPLACE, json.dumps(initial, ensure_ascii=False).encode("utf-8"))
        self.run_builder()
        self.run_builder()
        merged = json.loads((self.root / MARKETPLACE).read_bytes())
        for field in ("name", "displayName", "interface", "custom"):
            self.assertEqual(merged[field], initial[field])
        self.assertEqual([item for item in merged["plugins"] if item["name"] == "other-plugin"], [other])
        entries = [item for item in merged["plugins"] if item["name"] == "career-mentor"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/career-mentor"})
        self.assertEqual(entries[0]["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entries[0]["policy"]["authentication"], "ON_USE")

    def test_conflicting_marketplace_path_fails_before_any_output_write(self) -> None:
        conflict = {
            "name": "existing-marketplace",
            "plugins": [{"name": "career-mentor", "source": {"source": "local", "path": "./plugins/somewhere-else"}}],
        }
        self.write(MARKETPLACE, json.dumps(conflict).encode("utf-8"))
        before = self.snapshot()
        self.assertEqual(self.run_builder(expected=2)["status"], "error")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ARCHIVE).exists())
        self.assertFalse((self.root / "CHATGPT_INSTRUCTIONS.md").exists())

    def test_unowned_plugin_file_is_rejected_without_changing_old_archive(self) -> None:
        self.run_builder()
        archive_bytes = (self.root / ARCHIVE).read_bytes()
        checksum_bytes = (self.root / CHECKSUM).read_bytes()
        private = self.write(f"{PLUGIN}/private.md", b"PRIVATE-PLUGIN-FILE-MUST-SURVIVE")
        core = self.root / CANONICAL / "references/core.md"
        core.write_bytes(core.read_bytes() + b"\n<!-- isolated source update -->\n")
        before = self.snapshot()
        self.assertEqual(self.run_builder(expected=2)["status"], "error")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((self.root / ARCHIVE).read_bytes(), archive_bytes)
        self.assertEqual((self.root / CHECKSUM).read_bytes(), checksum_bytes)
        self.assertEqual(private.read_bytes(), b"PRIVATE-PLUGIN-FILE-MUST-SURVIVE")


if __name__ == "__main__":
    unittest.main()
