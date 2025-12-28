# course_arrange_add.py
# Usage: python course_arrange_add.py F7-106

import csv
import os
import re
import sys
from typing import Dict, List, Tuple, Optional
from Otools.get_data_path import get_data_path


COURSEINFO_CSV = get_data_path("CourseInfo.csv")
COURSEARRANGE_CSV = get_data_path("CourseArrange.csv")
TOOL_PROMPT = '4.course_arranger：輸入課程代碼，這個工具會協助預排與加選。格式 {{ "course_code": "課程代碼" }}'

PERIODS = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DAY_MAP = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
}

def _period_to_idx(p: str) -> int:
    p = (p or "").strip().upper()
    if p not in PERIODS:
        raise ValueError(f"Invalid period: {p}")
    return PERIODS.index(p)

def _expand_period_range(start_p: str, end_p: Optional[str]) -> List[str]:
    s = _period_to_idx(start_p)
    e = _period_to_idx(end_p) if end_p else s
    if e < s:
        s, e = e, s
    return PERIODS[s:e+1]

def parse_time_slots(time_str: str) -> List[Tuple[str, str]]:
    """
    Parse time strings like:
      [4]2~4
      [3]3
      [1]2~3, [2]3~4, [4]3~4, [5]3~4
    Return list of (day_name, period) pairs
    """
    if not time_str:
        return []

    s = time_str.strip()
    pattern = r"\[(\d)\]\s*([0-9A-Da-d])(?:\s*~\s*([0-9A-Da-d]))?"
    matches = re.findall(pattern, s)

    out: List[Tuple[str, str]] = []
    for day_num, start_p, end_p in matches:
        day_name = DAY_MAP.get(day_num)
        if not day_name:
            continue
        for p in _expand_period_range(start_p, end_p):
            out.append((day_name, p))
    return out

def read_course_from_courseinfo(course_code: str, courseinfo_csv: str = COURSEINFO_CSV) -> Dict[str, str]:
    """
    Supports CourseInfo.csv with or without header.
    No-header expected columns:
      0: course_code, 1: time, 2: course_name, 3: credits, 4: college_code,
      5: dept_code, 6: grade, 7: required
    Header supported:
      course_code,time,course_name,credits,college_code,dept_code,grade,required
    """
    course_code = course_code.strip()

    if not os.path.exists(courseinfo_csv):
        raise FileNotFoundError(f"Missing {courseinfo_csv}")

    with open(courseinfo_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise FileNotFoundError(f"{courseinfo_csv} is empty")

    header_like = [c.strip().lower() for c in rows[0]]
    has_header = ("course_code" in header_like) or ("course_name" in header_like) or ("time" in header_like)

    if has_header:
        with open(courseinfo_csv, "r", encoding="utf-8-sig", newline="") as f:
            dr = csv.DictReader(f)
            for r in dr:
                if (r.get("course_code") or "").strip() == course_code:
                    return {
                        "course_code": (r.get("course_code") or "").strip(),
                        "time": (r.get("time") or "").strip(),
                        "course_name": (r.get("course_name") or "").strip(),
                    }
    else:
        for r in rows:
            if not r:
                continue
            if r[0].strip() == course_code:
                return {
                    "course_code": r[0].strip(),
                    "time": (r[1].strip() if len(r) > 1 else ""),
                    "course_name": (r[2].strip() if len(r) > 2 else ""),
                }

    raise KeyError("not found")

def ensure_course_arrange(coursearrange_csv: str = COURSEARRANGE_CSV) -> None:
    # Create if missing/empty
    if os.path.exists(coursearrange_csv) and os.path.getsize(coursearrange_csv) > 0:
        return

    with open(coursearrange_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Period"] + DAY_ORDER)
        for p in PERIODS:
            w.writerow([p] + [""] * len(DAY_ORDER))

def load_course_arrange(coursearrange_csv: str = COURSEARRANGE_CSV) -> Dict[str, Dict[str, str]]:
    ensure_course_arrange(coursearrange_csv)

    table: Dict[str, Dict[str, str]] = {p: {d: "" for d in DAY_ORDER} for p in PERIODS}

    with open(coursearrange_csv, "r", encoding="utf-8-sig", newline="") as f:
        dr = csv.DictReader(f)
        for row in dr:
            period = (row.get("Period") or "").strip().upper()
            if period in table:
                for d in DAY_ORDER:
                    table[period][d] = (row.get(d) or "").strip()

    return table

def save_course_arrange(table: Dict[str, Dict[str, str]], coursearrange_csv: str = COURSEARRANGE_CSV) -> None:
    with open(coursearrange_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Period"] + DAY_ORDER)
        for p in PERIODS:
            w.writerow([p] + [table[p][d] for d in DAY_ORDER])

def add_course_by_code(course_code: str,
                       courseinfo_csv: str = COURSEINFO_CSV,
                       coursearrange_csv: str = COURSEARRANGE_CSV) -> str:
    try:
        course = read_course_from_courseinfo(course_code, courseinfo_csv=courseinfo_csv)
    except KeyError:
        return "Error: Can't Not Find Course (not in CourseInfo.csv)"
    except Exception as e:
        return f"Error: failed to read CourseInfo.csv: {e}"

    code = course["course_code"]
    name = course["course_name"]
    time_str = course["time"]

    slots = parse_time_slots(time_str)
    if not slots:
        return f"Error: find course {code} but time slot failed：{time_str!r}"

    table = load_course_arrange(coursearrange_csv)
    token = f"{code}:{name}"

    for day, period in slots:
        cell = table[period][day]
        if not cell:
            table[period][day] = token
        else:
            parts = cell.split("||")
            if token not in parts:
                table[period][day] = cell + "||" + token

    save_course_arrange(table, coursearrange_csv)
    return f"OK: added {code} ({len(slots)} cells) -> {coursearrange_csv}"

def course_arranger(course_code):
    msg = add_course_by_code(course_code, COURSEINFO_CSV, COURSEARRANGE_CSV)
    return msg