"""Create missing, blank learning records without replacing existing files."""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import stat


def blank_records(today):
    metadata = (
        f"- 初始化日期：{today}（Asia/Shanghai；仅为建档日期，不是训练证据）\n"
    )
    return {
        "profile.md": "# 学生档案\n\n" + metadata + """
## 默认训练目标，可更正

以下来自仓库公开默认目标，不代表本次用户的新自述：

- 届别与专业：2027届软件工程。
- 求职城市：南京。
- 优先方向：Python 后端与 AI 应用。
- 备选方向：Java 初级开发与软件测试。

## 待确认背景

- 姓名、学校、已有能力、学习时长与项目经历：待确认。
- 学习偏好与约束：待确认。
- 能力评价：未评估。

## 背景修订历史

尚无用户背景修订记录。
""",
        "progress.md": "# 学习进度\n\n" + metadata + """
## 当前状态

<!-- CURRENT_STATE_START -->
- 会话ID：无。
- 当前模式：未开始。
- 环节：待初始测评。
- 状态：未开始训练。
- 题目ID：无。
- 题目原文：尚未出题。
- 提示等级：0（尚未出题）。
- 完整答案展示：否。
- 外部AI使用：待确认（尚未开始训练）。
- 关联薄弱点/复测槽位：无。
- 下一步：初始测评，先提出一道主要题目并等待学生回答。
<!-- CURRENT_STATE_END -->

## 暂停状态

无。

## 当前能力快照

| 能力维度 | 当前评价 | 证据 |
| --- | --- | --- |
| 独立编程 | 未评估 | 无 |
| 算法思维 | 未评估 | 无 |
| 工程实践 | 未评估 | 无 |
| 面试表达 | 未评估 | 无 |
| 项目理解 | 未评估 | 无 |
| Python与计算机基础 | 未评估 | 无 |

## 训练历史

尚无实际训练、回答尝试或测试记录。
""",
        "weaknesses.md": "# 薄弱点与复测\n\n" + metadata + """
## 当前薄弱点索引

尚无实际观察，未评估的能力不视为薄弱点。

## 当前复测队列

空。未发生真实错误，不生成复测锚点或计划日期。

## 证据与状态历史

尚无薄弱点证据、复测结果或状态变化。
""",
        "interviews.md": "# 面试记录\n\n" + metadata + """
## 当前或最近面试

未发生。

## 能力评价

未评估。

## 面试历史

尚无实际面试、回答、追问或评分记录。
""",
        "learning-plan.md": "# 动态学习计划\n\n" + metadata + """
## 当前阶段与下一步

- 当前阶段：第1阶段，初始诊断（尚未开始）。
- 下一项任务：以一道主要题目开始初始测评，等待学生先分析或作答。
- 短期优先级：先取得真实证据，再确定补弱重点。

## 五阶段框架

以下是待调整的训练方向，不是已完成事项或固定进度安排。

| 阶段 | 方向 | 调整依据 |
| --- | --- | --- |
| 1 | Python基础与编程逻辑，先做初始诊断 | 真实回答、代码与已执行测试 |
| 2 | 数据结构、算法与计算机基础 | 具体错误证据及复测结果 |
| 3 | Python后端与数据库 | 可运行服务、数据建模与可核验贡献 |
| 4 | AI应用、Agent与工程项目 | 实际项目验收、设计取舍与故障处理 |
| 5 | 校招准备与持续复测 | 用户目标、已核实岗位信息与延迟复测 |

阶段与任务根据真实证据动态调整，不机械推进。

## 计划调整历史

尚无基于实际训练的计划调整记录。
""",
    }


def check_path(path, directory):
    """Reject links/reparse points and incompatible existing path types."""
    parts = list(reversed(path.parents)) + [path]
    for part in parts:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        reparse = getattr(info, "st_file_attributes", 0) & getattr(
            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
        )
        if stat.S_ISLNK(info.st_mode) or reparse:
            raise ValueError(f"拒绝链接或 junction 路径：{part}")
        needs_directory = part != path or directory
        expected_type = stat.S_ISDIR if needs_directory else stat.S_ISREG
        if not expected_type(info.st_mode):
            raise ValueError(f"路径类型不符合要求：{part}")


def initialize(root):
    root = Path(os.path.abspath(root))
    # Shanghai has a fixed UTC+08:00 offset; this works without external tzdata.
    today = datetime.now(timezone(timedelta(hours=8), "Asia/Shanghai")).date()
    records = blank_records(today)
    directories = [root, root / "data", root / "exercises", root / "projects"]
    files = [(root / "data" / name, content) for name, content in records.items()]

    # Inspect every planned destination before creating anything.
    for directory in directories:
        check_path(directory, directory=True)
    for path, _ in files:
        check_path(path, directory=False)

    for directory in directories:
        check_path(directory, directory=True)
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
    result = {"created": [], "skipped": []}
    for path, content in files:
        check_path(path, directory=False)
        relative = path.relative_to(root).as_posix()
        try:
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        except FileExistsError:
            result["skipped"].append(relative)
        else:
            result["created"].append(relative)
    return result


def main():
    parser = argparse.ArgumentParser(description="仅补齐缺失的空白学习档案。")
    parser.add_argument("--root", type=Path, default=Path(__file__).absolute().parents[1])
    args = parser.parse_args()
    try:
        result = initialize(args.root)
    except (OSError, ValueError) as error:
        parser.exit(1, f"初始化失败：{error}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
