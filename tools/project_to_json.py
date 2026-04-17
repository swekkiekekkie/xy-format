#!/usr/bin/env python3
"""Extract decoded intent from an .xy file as a JSON BuildSpec.

Usage:
    python tools/project_to_json.py <input.xy> [-o <out.json>]

The output is a ``BuildSpec`` payload that, when compiled via
``tools/build_xy_from_json.py`` against the same template, produces
functionally equivalent bytes. See ``xy/project_to_json.py`` for the
round-trip contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from xy.project_to_json import project_to_json


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract a .xy file as a JSON BuildSpec.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a .xy file to read.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSON to this path (default: stdout).",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help=(
            "Path to embed as the scaffold ``template`` field. "
            "Defaults to the input path — round-trip applies extracted "
            "intent back on top of the original bytes."
        ),
    )
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    in_path = args.input.expanduser().resolve()
    template = (args.template or args.input).expanduser().resolve()
    payload = project_to_json(in_path.read_bytes(), template_path=template)
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        out_path = args.output.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(serialized, encoding="utf-8")
        print(f"wrote {out_path}")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
