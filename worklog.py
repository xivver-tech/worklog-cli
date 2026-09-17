#!/usr/bin/env python3
"""
Worklog CLI – serious time tracking
- Start / stop timers with project + tags
- Manual entries
- Daily / weekly / project reports
- Export CSV
"""

import json
import sys
import argparse
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict

DATA_FILE = Path(__file__).parent / "worklog.json"

def load():
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"entries": [], "active": None}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now():
    return datetime.now().isoformat(timespec="seconds")

def start(project, tags=None, note=""):
    data = load()
    if data.get("active"):
        print("Already tracking something. Stop it first.")
        return
    data["active"] = {
        "project": project.strip(),
        "tags": [t.strip().lower() for t in (tags or [])],
        "note": note.strip(),
        "start": now()
    }
    save(data)
    print(f"▶ Started: {project}")

def stop():
    data = load()
    active = data.get("active")
    if not active:
        print("Nothing is running.")
        return
    end = now()
    start_dt = datetime.fromisoformat(active["start"])
    end_dt = datetime.fromisoformat(end)
    minutes = int((end_dt - start_dt).total_seconds() / 60)

    entry = {
        "id": len(data["entries"]) + 1,
        "project": active["project"],
        "tags": active.get("tags", []),
        "note": active.get("note", ""),
        "start": active["start"],
        "end": end,
        "minutes": max(minutes, 1)
    }
    data["entries"].append(entry)
    data["active"] = None
    save(data)
    print(f"■ Stopped: {entry['project']} ({entry['minutes']} min)")

def status():
    data = load()
    active = data.get("active")
    if not active:
        print("Not tracking anything.")
        return
    start_dt = datetime.fromisoformat(active["start"])
    mins = int((datetime.now() - start_dt).total_seconds() / 60)
    print(f"▶ {active['project']}  ({mins} min so far)")
    if active.get("note"):
        print(f"  {active['note']}")

def report(days=7):
    data = load()
    entries = data.get("entries", [])
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent = [e for e in entries if e["start"] >= cutoff]

    if not recent:
        print(f"No entries in the last {days} days.")
        return

    by_project = defaultdict(int)
    total = 0
    for e in recent:
        by_project[e["project"]] += e["minutes"]
        total += e["minutes"]

    print(f"\nReport — last {days} days\n")
    for proj, mins in sorted(by_project.items(), key=lambda x: -x[1]):
        hrs = mins / 60
        print(f"  {proj:<25} {mins:>5} min  ({hrs:.1f} h)")
    print("-" * 45)
    print(f"  {'TOTAL':<25} {total:>5} min  ({total/60:.1f} h)\n")

def export_csv(path="worklog.csv"):
    data = load()
    entries = data.get("entries", [])
    lines = ["id,project,tags,note,start,end,minutes"]
    for e in entries:
        tags = "|".join(e.get("tags", []))
        note = e.get("note", "").replace(",", " ")
        lines.append(f'{e["id"]},{e["project"]},{tags},{note},{e["start"]},{e["end"]},{e["minutes"]}')
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ Exported {len(entries)} entries to {path}")

def main():
    parser = argparse.ArgumentParser(description="Worklog – time tracking")
    sub = parser.add_subparsers(dest="cmd")

    p_start = sub.add_parser("start", help="Start tracking")
    p_start.add_argument("project")
    p_start.add_argument("--tags", nargs="*", default=[])
    p_start.add_argument("-n", "--note", default="")

    sub.add_parser("stop", help="Stop current timer")
    sub.add_parser("status", help="Show current timer")

    p_report = sub.add_parser("report", help="Show report")
    p_report.add_argument("--days", type=int, default=7)

    p_export = sub.add_parser("export", help="Export CSV")
    p_export.add_argument("-o", "--output", default="worklog.csv")

    args = parser.parse_args()

    if args.cmd == "start":
        start(args.project, args.tags, args.note)
    elif args.cmd == "stop":
        stop()
    elif args.cmd == "status":
        status()
    elif args.cmd == "report":
        report(args.days)
    elif args.cmd == "export":
        export_csv(args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
