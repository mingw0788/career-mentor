#!/usr/bin/env python3
"""Build the public CareerMentor artifacts using only the Python standard library.

The canonical sources live in .agents/skills/career-mentor.  Nothing under
data/, exercises/, projects/, or handoff/latest-report.md is read or changed.
Run with --check for a read-only freshness check, or --root for an isolated copy.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import zipfile


VERSION = "2.1.0"
CANONICAL = ".agents/skills/career-mentor"
PLUGIN = "plugins/career-mentor"
MARKETPLACE = ".agents/plugins/marketplace.json"
ARCHIVE = "dist/career-mentor-skills-only.zip"
CHECKSUM = "dist/career-mentor-skills-only.sha256"
REFERENCES = ("core", "training", "interviews", "records", "roadmap", "handoff")
# Explicitly review this list when a new public skill resource is introduced.
SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    *(f"references/{name}.md" for name in REFERENCES),
    "assets/record-templates.md",
    "assets/report-template.md",
    "assets/chatgpt-adapter.md",
    "scripts/review_schedule.py",
)
DESCRIPTION = "面向软件工程学生的编程训练、技术面试、项目辅导与学习档案维护。"
INTERFACE = {
    "displayName": "CareerMentor V2",
    "shortDescription": "软件工程学生的编程训练、技术面试与求职成长导师",
    "defaultPrompt": ["开始今日训练，先读取已有学习档案。", "模拟压力面试"],
}
GENERATED = "<!-- 由 tools/build_distribution.py 从 .agents/skills/career-mentor/ 生成；请修改源文件后重建。 -->\n\n"
RELATIVE_LINK = re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(?:\s+"[^"\n]*")?\)')


class BuildError(Exception):
    """A source or output failed a required safety or consistency check."""


def safe_path(root: Path, relative: str) -> Path:
    """Reject traversal, symlinks and Windows junctions, including parent links."""
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or "\\" in relative or ":" in relative:
        raise BuildError(f"不安全的相对路径：{relative}")
    candidate = root
    for part in parts.parts:
        candidate /= part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & reparse:
            raise BuildError(f"不允许链接或重解析点：{relative}")
    if not candidate.resolve().is_relative_to(root):
        raise BuildError(f"路径超出工作区：{relative}")
    return candidate


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_sources(root: Path) -> dict[str, bytes]:
    sources = {}
    for relative in SKILL_FILES:
        if PurePosixPath(relative).suffix not in {".md", ".py", ".yaml"}:
            raise BuildError(f"技能白名单含不支持的扩展名：{relative}")
        path = safe_path(root, f"{CANONICAL}/{relative}")
        if not path.is_file():
            raise BuildError(f"缺少 canonical 源文件：{CANONICAL}/{relative}")
        sources[relative] = path.read_bytes()
    return sources


def source_text(sources: dict[str, bytes], relative: str) -> str:
    try:
        return sources[relative].decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").rstrip()
    except UnicodeDecodeError as error:
        raise BuildError(f"源文件必须是 UTF-8：{relative}") from error


def without_relative_links(content: str) -> str:
    """Keep external links; make local links readable in the merged upload file."""
    def replace(match: re.Match[str]) -> str:
        label, target = match.groups()
        if target.startswith("//") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            return match.group(0)
        filename = PurePosixPath(target.split("#", 1)[0].split("?", 1)[0]).name
        return label if not filename or filename in label else f"{label}（{filename}）"

    return RELATIVE_LINK.sub(replace, content)


def merge_marketplace(root: Path) -> bytes:
    path = safe_path(root, MARKETPLACE)
    if path.exists():
        if not path.is_file():
            raise BuildError(f"marketplace 不是普通文件：{MARKETPLACE}")
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise BuildError("已有 marketplace JSON 无效；未覆盖") from error
        if not isinstance(value, dict):
            raise BuildError("已有 marketplace 必须是 JSON 对象；未覆盖")
    else:
        value = {}
    entries = value.setdefault("plugins", [])
    interface = value.setdefault("interface", {})
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        raise BuildError("已有 marketplace.plugins 必须是对象列表；未覆盖")
    if not isinstance(interface, dict):
        raise BuildError("已有 marketplace.interface 必须是对象；未覆盖")
    matches = [item for item in entries if item.get("name") == "career-mentor"]
    if len(matches) > 1:
        raise BuildError("marketplace 中 career-mentor 重复；未覆盖")
    if matches:
        entry = matches[0]
        source = entry.get("source")
        if (not isinstance(source, dict) or source.get("source") != "local"
                or not isinstance(source.get("path"), str)
                or PurePosixPath(source["path"]) != PurePosixPath("./plugins/career-mentor")):
            raise BuildError("marketplace 中同名 career-mentor 指向其它来源或路径；未覆盖")
    else:
        entry = {"name": "career-mentor"}
        entries.append(entry)
    policy = entry.setdefault("policy", {})
    if not isinstance(policy, dict):
        raise BuildError("已有 career-mentor.policy 必须是对象；未覆盖")
    value.setdefault("name", "career-mentor-local")
    interface.setdefault("displayName", "CareerMentor本地插件")
    entry["source"] = {"source": "local", "path": "./plugins/career-mentor"}
    policy.update(installation="AVAILABLE", authentication="ON_USE")
    entry["category"] = "Productivity"
    return json_bytes(value)


def plugin_manifest(compatibility: bool = False) -> bytes:
    value = {
        "name": "career-mentor",
        "version": VERSION,
        "description": DESCRIPTION,
        "author": {"name": "CareerMentor"},
    }
    if compatibility:
        value.update(skills="./skills/", interface=INTERFACE)
    else:
        value = {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            **value,
            "extensions": {"com.openai": {"interface": INTERFACE}},
        }
    return json_bytes(value)


def make_zip(files: dict[str, bytes]) -> bytes:
    """Fixed order, timestamp, permissions and storage avoid machine-specific ZIPs."""
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for relative, content in sorted(files.items()):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, content)
    return stream.getvalue()


def expected_outputs(root: Path) -> tuple[dict[str, bytes], set[str], int, str]:
    sources = read_sources(root)
    core = source_text(sources, "references/core.md")
    instructions = (
        GENERATED
        + source_text(sources, "assets/chatgpt-adapter.md")
        + "\n\n<!-- CORE_STANDARD_START -->\n\n"
        + core
        + "\n\n<!-- CORE_STANDARD_END -->\n\n"
        + source_text(sources, "assets/report-template.md")
        + "\n"
    )
    if len(instructions) >= 8000:
        raise BuildError(f"ChatGPT 指令共 {len(instructions)} 字符，必须少于 8000；请缩减源适配器或模板")
    reference_sections = [GENERATED + "# CareerMentor ChatGPT 完整参考\n"]
    for name in REFERENCES:
        relative = f"references/{name}.md"
        reference_sections.append(f"## 来源：{relative}\n\n" + without_relative_links(source_text(sources, relative)))
    reference_sections.append("## 来源：assets/record-templates.md\n\n" + without_relative_links(source_text(sources, "assets/record-templates.md")))
    instructions_bytes = instructions.encode("utf-8")
    reference_bytes = ("\n\n".join(reference_sections).rstrip() + "\n").encode("utf-8")
    outputs = {
        "CHATGPT_INSTRUCTIONS.md": instructions_bytes,
        "handoff/chatgpt-project-instructions.md": instructions_bytes,
        "handoff/CHATGPT_REFERENCE.md": reference_bytes,
        "templates/LEARNING_RECORD_TEMPLATE.md": sources["assets/record-templates.md"],
        "templates/TRAINING_REPORT_TEMPLATE.md": sources["assets/report-template.md"],
        MARKETPLACE: merge_marketplace(root),
    }
    for name in REFERENCES:
        content = source_text(sources, f"references/{name}.md")
        content = content.replace("../assets/report-template.md", "../templates/TRAINING_REPORT_TEMPLATE.md")
        content = content.replace("../assets/record-templates.md", "../templates/LEARNING_RECORD_TEMPLATE.md")
        outputs[f"standards/{name}.md"] = (GENERATED + content + "\n").encode("utf-8")
    plugin_files = {
        "plugin.json": plugin_manifest(),
        ".codex-plugin/plugin.json": plugin_manifest(compatibility=True),
        "assets/CHATGPT_INSTRUCTIONS.md": instructions_bytes,
        "assets/CHATGPT_REFERENCE.md": reference_bytes,
    }
    plugin_files.update({f"skills/career-mentor/{relative}": data for relative, data in sources.items()})
    outputs.update({f"{PLUGIN}/{relative}": data for relative, data in plugin_files.items()})
    archive = make_zip(plugin_files)
    digest = hashlib.sha256(archive).hexdigest()
    outputs[ARCHIVE] = archive
    outputs[CHECKSUM] = f"{digest}  {PurePosixPath(ARCHIVE).name}\n".encode("ascii")
    return outputs, set(plugin_files), len(instructions), digest


def check_plugin_tree(root: Path, allowed: set[str]) -> None:
    """Refuse to package or silently erase any unowned files or linked folders."""
    plugin_root = safe_path(root, PLUGIN)
    if not plugin_root.exists():
        return
    if not plugin_root.is_dir():
        raise BuildError(f"插件输出路径不是目录：{PLUGIN}")

    def fail(error: OSError) -> None:
        raise error

    for directory, subdirectories, filenames in os.walk(plugin_root, followlinks=False, onerror=fail):
        parent = Path(directory)
        for name in subdirectories + filenames:
            item = parent / name
            relative = item.relative_to(root).as_posix()
            safe_path(root, relative)
            if name in filenames:
                if not item.is_file():
                    raise BuildError(f"插件目录含非普通文件：{relative}")
                if item.relative_to(plugin_root).as_posix() not in allowed:
                    raise BuildError(f"插件目录含白名单外文件：{relative}；请核对后手动移出，生成器不会删除")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".career-mentor-build-", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="从 canonical Skill 生成 CareerMentor 双平台资料与 skills-only 插件；不读取或修改个人档案。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="工作区根目录；可指向 .verification 下的隔离副本")
    parser.add_argument("--check", action="store_true", help="只读检查全部生成件、插件白名单和 ZIP 是否与源文件一致")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise BuildError("工作区根路径必须是目录")
        outputs, allowed, instruction_chars, digest = expected_outputs(root)
        check_plugin_tree(root, allowed)
        changed = []
        for relative, content in outputs.items():
            path = safe_path(root, relative)
            if path.exists() and not path.is_file():
                raise BuildError(f"输出路径不是普通文件：{relative}")
            if not path.exists() or path.read_bytes() != content:
                changed.append(relative)
        if not args.check:
            # All sources, conflicts, output paths and plugin extras were checked first.
            for relative in changed:
                atomic_write(safe_path(root, relative), outputs[relative])
        summary = {
            "status": "outdated" if args.check and changed else "ok",
            "mode": "check" if args.check else "build",
            "outputs": len(outputs),
            "changed": changed if args.check else len(changed),
            "plugin_files": len(allowed),
            "instructions_chars": instruction_chars,
            "archive": ARCHIVE,
            "sha256": digest,
        }
        print(json.dumps(summary, ensure_ascii=False))
        return 1 if args.check and changed else 0
    except (BuildError, OSError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
