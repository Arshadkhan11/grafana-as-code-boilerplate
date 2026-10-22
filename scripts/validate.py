#!/usr/bin/env python3
"""Fail CI if generated Grafana JSON is empty or missing required PromQL hooks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fail(msg: str) -> int:
    print(f"validate: {msg}", file=sys.stderr)
    return 1


def validate_dashboard(path: Path) -> int:
    data = json.loads(path.read_text())
    if data.get("schemaVersion", 0) < 30:
        return fail(f"{path}: schemaVersion too old")
    panels = data.get("panels") or []
    if not panels:
        return fail(f"{path}: no panels")
    titles = {p.get("title") for p in panels}
    for required in ("Request rate", "Error rate", "p99 latency"):
        if required not in titles:
            return fail(f"{path}: missing panel '{required}'")
    return 0


def validate_alerts(path: Path) -> int:
    data = json.loads(path.read_text())
    groups = data.get("groups")
    if groups is None:
        return fail(f"{path}: missing groups")
    if groups == []:
        return 0
    for group in groups:
        for rule in group.get("rules") or []:
            if not rule.get("title"):
                return fail(f"{path}: alert rule missing title")
            if "expr" not in json.dumps(rule):
                return fail(f"{path}: alert '{rule.get('title')}' has no expr")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=Path)
    args = parser.parse_args()
    dashboard = args.dir / "dashboard.json"
    alerts = args.dir / "alerts.json"
    if not dashboard.exists() or not alerts.exists():
        return fail(f"{args.dir}: run make render first")
    rc = validate_dashboard(dashboard)
    rc = validate_alerts(alerts) or rc
    if rc == 0:
        print(f"validate: OK {args.dir}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
