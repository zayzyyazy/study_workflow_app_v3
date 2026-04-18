#!/usr/bin/env python3
"""Quick sanity check after migrate_from_legacy.sh — run from V3 project root."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)

from app.config import APP_ROOT, COURSES_DIR, DATABASE_PATH  # noqa: E402


def main() -> None:
    db = DATABASE_PATH
    if not db.is_file():
        print("FAIL: no database at", db)
        sys.exit(1)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    for label, sql in [
        ("courses", "SELECT COUNT(*) FROM courses"),
        ("lectures", "SELECT COUNT(*) FROM lectures"),
        ("artifacts", "SELECT COUNT(*) FROM artifacts"),
        ("concepts", "SELECT COUNT(*) FROM concepts"),
        ("planner_schedule_items", "SELECT COUNT(*) FROM planner_schedule_items"),
    ]:
        try:
            n = cur.execute(sql).fetchone()[0]
            print(f"{label}: {n}")
        except sqlite3.OperationalError as e:
            print(f"{label}: (skip) {e}")

    cur.execute(
        "SELECT source_file_path FROM lectures LIMIT 5"
    )
    missing = 0
    for (rel,) in cur.fetchall():
        p = APP_ROOT / rel
        if not p.exists():
            # allow dir-only for some legacy rows
            if not p.parent.is_dir():
                missing += 1
                print("WARN missing path:", rel)
    conn.close()
    if not COURSES_DIR.is_dir():
        print("FAIL: courses dir missing:", COURSES_DIR)
        sys.exit(1)
    print("courses dir:", COURSES_DIR, "OK")
    if missing:
        print("FAIL:", missing, "lecture paths not found on disk")
        sys.exit(1)
    print("OK: sample paths exist on disk.")


if __name__ == "__main__":
    main()
