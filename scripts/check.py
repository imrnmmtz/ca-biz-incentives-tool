#!/usr/bin/env python3
"""Validate src/data.js, and optionally check its links against the source PDF.

    python3 scripts/check.py
    python3 scripts/check.py --pdf data/CA-BIG-2026-09.pdf

Checks:
  * every entry has all required fields
  * no duplicate names, all urls are https
  * with --pdf: every `url` matches the guide's own embedded hyperlink, in order

Exit code is non-zero if anything fails, so this works as a pre-commit hook.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data.js"

REQUIRED = ["name", "category", "body", "type", "eligibility",
            "total", "max", "timing", "email", "url", "summary", "detail"]

EXPECTED_CATEGORIES = {
    "Business Development & Business Support": 22,
    "Employment & Workforce": 6,
    "Equipment & Machinery": 11,
    "Financing & Start Up Support": 22,
    "Power & Utilities": 8,
}


def load_data() -> list[dict]:
    """Evaluate data.js with node and hand back plain Python dicts."""
    src = DATA.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(src + "\nprocess.stdout.write(JSON.stringify(INCENTIVES));\n")
        tmp = fh.name
    try:
        out = subprocess.run(["node", tmp], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("error: node is required to read src/data.js")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: src/data.js failed to parse\n{exc.stderr}")
    finally:
        pathlib.Path(tmp).unlink(missing_ok=True)
    return json.loads(out.stdout)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("&", "and")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=pathlib.Path,
                    help="also verify links against this guide PDF")
    args = ap.parse_args()

    items = load_data()
    problems: list[str] = []

    print(f"entries: {len(items)}")

    for i, it in enumerate(items):
        label = it.get("name", f"<entry {i}>")
        for key in REQUIRED:
            if not it.get(key):
                problems.append(f"{label}: missing `{key}`")
        url = it.get("url", "")
        if url and not url.startswith("https://"):
            problems.append(f"{label}: url is not https ({url})")

    names = [it.get("name") for it in items]
    for dupe in {n for n in names if names.count(n) > 1}:
        problems.append(f"duplicate name: {dupe}")

    counts: dict[str, int] = {}
    for it in items:
        counts[it.get("category", "?")] = counts.get(it.get("category", "?"), 0) + 1
    for cat, expected in EXPECTED_CATEGORIES.items():
        got = counts.get(cat, 0)
        flag = "ok" if got == expected else f"EXPECTED {expected}"
        print(f"  {cat:<42} {got:>3}  {flag}")
        if got != expected:
            problems.append(f"category count changed: {cat} ({got} vs {expected})")

    if args.pdf:
        sys.path.insert(0, str(ROOT / "scripts"))
        from extract_links import extract  # noqa: E402

        rows = [r for r in extract(args.pdf, 6, 21) if r["column"] == "name"]
        print(f"\npdf incentive links: {len(rows)}")
        if len(rows) != len(items):
            problems.append(f"pdf has {len(rows)} links but data.js has {len(items)} entries")
        else:
            for it, row in zip(items, rows):
                a, b = norm(it["name"]), norm(row["text"])
                if not (a.startswith(b[:22]) or b.startswith(a[:22])):
                    problems.append(f"order drift: data.js '{it['name']}' vs pdf '{row['text']}'")
                elif it["url"] != row["uri"]:
                    problems.append(
                        f"link mismatch for {it['name']}\n"
                        f"      data.js: {it['url']}\n"
                        f"      pdf    : {row['uri']}")

    print()
    if problems:
        print(f"FAILED — {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
