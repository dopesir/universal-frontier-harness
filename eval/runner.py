#!/usr/bin/env python3
"""Benchmark evaluation runner.

Loads calibrated tasks from eval/tasks/ and validates agent trajectories
and evidence ledgers against objective criteria.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.contract import validate_contract


def run_benchmarks(tasks_dir: str | Path) -> dict:
    t_dir = Path(tasks_dir)
    tasks = list(t_dir.glob("*.json"))
    results = {"total": len(tasks), "passed": 0, "failed": 0, "tasks": []}

    for task_file in tasks:
        try:
            with open(task_file, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
        except Exception as e:
            results["failed"] += 1
            results["tasks"].append({"id": task_file.stem, "status": "FAIL", "error": str(e)})
            continue

        errors = validate_contract(data)
        if not errors:
            results["passed"] += 1
            results["tasks"].append({"id": data.get("id"), "name": data.get("name"), "status": "PASS"})
        else:
            results["failed"] += 1
            results["tasks"].append({"id": data.get("id", task_file.stem), "status": "FAIL", "errors": errors})

    return results


if __name__ == "__main__":
    tasks_path = Path(__file__).resolve().parent / "tasks"
    res = run_benchmarks(tasks_path)
    print(f"BENCHMARK_EVALUATION_REPORT:")
    print(f"Total Tasks: {res['total']} | Passed: {res['passed']} | Failed: {res['failed']}")
    for t in res["tasks"]:
        print(f"  [{t['status']}] {t.get('id')}: {t.get('name', '')}")
    sys.exit(0 if res["failed"] == 0 else 1)
