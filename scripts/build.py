#!/usr/bin/env python3
"""Assemble src/app.html + src/data.js into a single self-contained dist/index.html.

The shipped artifact is deliberately one file with no dependencies, so it can be
dropped on any static host (or opened straight from disk). This script just
inlines the dataset into the placeholder.

    python3 scripts/build.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHELL = ROOT / "src" / "app.html"
DATA = ROOT / "src" / "data.js"
# GitHub Pages serves from the repo root or /docs only, so the build
# output lives in docs/ rather than a conventional dist/.
OUT = ROOT / "docs" / "index.html"

PLACEHOLDER = "/*DATA*/"


def main() -> int:
    shell = SHELL.read_text(encoding="utf-8")
    data = DATA.read_text(encoding="utf-8")

    if PLACEHOLDER not in shell:
        print(f"error: {PLACEHOLDER} placeholder missing from {SHELL}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(shell.replace(PLACEHOLDER, data), encoding="utf-8")

    kb = OUT.stat().st_size / 1024
    print(f"built {OUT.relative_to(ROOT)}  ({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
