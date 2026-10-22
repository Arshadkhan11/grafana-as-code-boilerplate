#!/usr/bin/env python3
"""Render Grafana JSON from a service YAML + templates.

Placeholders are {{dotted.keys}} matching the YAML document.
Boolean flags become JSON true/false. Missing keys become empty string.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

PLACEHOLDER = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")


def flatten(node: object, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(value, path))
    elif isinstance(node, list):
        out[prefix] = json.dumps(node)
        for i, value in enumerate(node):
            out.update(flatten(value, f"{prefix}.{i}"))
    elif isinstance(node, bool):
        out[prefix] = "true" if node else "false"
    elif node is None:
        out[prefix] = ""
    else:
        out[prefix] = str(node)
    return out


def substitute(template: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            print(f"warn: missing placeholder {key}", file=sys.stderr)
            return ""
        return values[key]

    return PLACEHOLDER.sub(repl, template)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--templates",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates",
    )
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())
    values = flatten(config)
    args.out.mkdir(parents=True, exist_ok=True)

    mapping = {
        "dashboard.json.tmpl": "dashboard.json",
        "alerts.json.tmpl": "alerts.json",
    }
    for tmpl_name, out_name in mapping.items():
        raw = (args.templates / tmpl_name).read_text()
        rendered = substitute(raw, values)
        parsed = json.loads(rendered)
        if out_name == "alerts.json" and str(values.get("alerts.enabled", "true")).lower() == "false":
            parsed = {"groups": []}
        (args.out / out_name).write_text(json.dumps(parsed, indent=2) + "\n")
        print(f"wrote {args.out / out_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
