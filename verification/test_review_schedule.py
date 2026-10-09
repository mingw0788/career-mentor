"""对复测 CLI 进行外部行为测试；不读写学生档案，仅使用标准库。"""

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/career-mentor/scripts/review_schedule.py"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), *args],
        text=True, encoding="utf-8", capture_output=True, timeout=10,
    )


def schedule(anchor, today, *flags):
    result = run_cli("--anchor", anchor, "--today", today, *flags)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    value = json.loads(result.stdout)
    return {item["id"]: item for item in value["任务"]}


class ReviewScheduleTests(unittest.TestCase):
    def test_next_session_is_event_even_after_long_absence(self):
        tasks = schedule("2026-10-01", "2026-11-01")
        self.assertEqual(tasks["next_session"]["状态"], "待下次训练")
        self.assertIsNone(tasks["next_session"]["计划日期"])
        self.assertIsNone(tasks["next_session"]["逾期天数"])

    def test_before_due_dates(self):
        tasks = schedule("2026-10-08", "2026-10-08")
        self.assertEqual(tasks["day3"]["计划日期"], "2026-10-11")
        self.assertEqual(tasks["day7"]["计划日期"], "2026-10-15")
        self.assertEqual(tasks["day3"]["状态"], "待复测")

    def test_due_today_and_overdue_are_distinct(self):
        tasks = schedule("2026-10-01", "2026-10-08")
        self.assertEqual(tasks["day3"]["状态"], "逾期")
        self.assertEqual(tasks["day3"]["逾期天数"], 4)
        self.assertEqual(tasks["day7"]["状态"], "今日到期")
        self.assertEqual(tasks["day7"]["逾期天数"], 0)

    def test_completed_flags_do_not_change_original_dates(self):
        tasks = schedule("2026-10-01", "2026-10-20", "--next-session-completed",
                         "--day3-completed", "--day7-completed")
        self.assertTrue(all(t["状态"] == "已完成" for t in tasks.values()))
        self.assertEqual(tasks["day3"]["计划日期"], "2026-10-04")
        self.assertEqual(tasks["day7"]["计划日期"], "2026-10-08")

    def test_one_completed_flag_does_not_complete_others(self):
        tasks = schedule("2026-10-01", "2026-10-20", "--day3-completed")
        self.assertEqual(tasks["day3"]["状态"], "已完成")
        self.assertEqual(tasks["day7"]["状态"], "逾期")
        self.assertEqual(tasks["next_session"]["状态"], "待下次训练")

    def test_leap_day_and_year_boundary(self):
        leap = schedule("2028-02-27", "2028-02-29")
        self.assertEqual(leap["day3"]["计划日期"], "2028-03-01")
        self.assertEqual(leap["day7"]["计划日期"], "2028-03-05")
        year = schedule("2026-12-29", "2026-12-30")
        self.assertEqual(year["day3"]["计划日期"], "2027-01-01")
        self.assertEqual(year["day7"]["计划日期"], "2027-01-05")

    def test_invalid_input_fails_without_traceback(self):
        cases = [
            ("--anchor", "2026-2-03", "--today", "2026-10-08"),
            ("--anchor", "2026-02-30", "--today", "2026-10-08"),
            ("--anchor", "2026-10-09", "--today", "2026-10-08"),
            ("--anchor", "9999-12-29", "--today", "9999-12-29"),
            ("--anchor", "2026-10-08"),
            ("--anchor", "2026-10-08", "--today", "2026-10-08", "--unknown"),
            ("--anc", "2026-10-08", "--today", "2026-10-08"),
        ]
        for args in cases:
            with self.subTest(args=args):
                result = run_cli(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
