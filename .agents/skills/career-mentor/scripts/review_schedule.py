"""计算间隔复测候选计划；不读取或修改学习档案。"""

import argparse
import json
import re
from datetime import date, timedelta


def iso_date(value):
    """只接受严格 YYYY-MM-DD，避免隐式时区或宽松日期。"""
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise argparse.ArgumentTypeError("日期必须使用 YYYY-MM-DD 格式")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期不存在或超出支持范围") from exc


def dated_task(task_id, label, due, today, completed):
    """任务完成状态由调用方依据真实证据显式传入。"""
    if completed:
        status = "已完成"
    elif due < today:
        status = "逾期"
    elif due == today:
        status = "今日到期"
    else:
        status = "待复测"
    return {
        "id": task_id,
        "类型": "日期任务",
        "任务": label,
        "计划日期": due.isoformat(),
        "状态": status,
        "逾期天数": max(0, (today - due).days) if not completed else 0,
        "说明": "完成标记需有真实复测记录；完成任务不等于知识已掌握。",
    }


def build_schedule(anchor, today, next_session_completed=False,
                   day3_completed=False, day7_completed=False):
    if anchor > today:
        raise ValueError("首次错误日期不能晚于今天")
    # 提前验证最大日期边界，使 CLI 仍以明确信息退出而非回溯异常。
    try:
        day3 = anchor + timedelta(days=3)
        day7 = anchor + timedelta(days=7)
    except OverflowError as exc:
        raise ValueError("首次错误日期过晚，无法计算第 3/7 天任务") from exc
    return {
        "原复测锚点": anchor.isoformat(),
        "计算日期": today.isoformat(),
        "日期规则": "纯本地自然日：首次错误日期 +3 天、+7 天；不涉及时间或时区转换。",
        "任务": [
            {
                "id": "next_session",
                "类型": "事件任务",
                "任务": "下一次训练复测",
                "计划日期": None,
                "状态": "已完成" if next_session_completed else "待下次训练",
                "逾期天数": None,
                "说明": "由下一次实际训练触发；不能仅凭日期判断到期或逾期。",
            },
            dated_task("day3", "第 3 天再次复测", day3, today, day3_completed),
            dated_task("day7", "第 7 天变式考核", day7, today, day7_completed),
        ],
        "使用说明": "仅生成候选计划，不读取或更新档案，不发提醒；动态调整需另记录证据、旧计划与新计划，不能自动重置原锚点。",
    }


def main():
    parser = argparse.ArgumentParser(description="计算 CareerMentor 间隔复测候选计划", allow_abbrev=False)
    parser.add_argument("--anchor", required=True, type=iso_date, help="首次错误日期 YYYY-MM-DD")
    parser.add_argument("--today", required=True, type=iso_date, help="本次计算日期 YYYY-MM-DD")
    parser.add_argument("--next-session-completed", action="store_true", help="已依据真实证据完成下一次训练复测")
    parser.add_argument("--day3-completed", action="store_true", help="已依据真实证据完成第 3 天复测")
    parser.add_argument("--day7-completed", action="store_true", help="已依据真实证据完成第 7 天变式考核")
    args = parser.parse_args()
    try:
        result = build_schedule(args.anchor, args.today, args.next_session_completed,
                                args.day3_completed, args.day7_completed)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
