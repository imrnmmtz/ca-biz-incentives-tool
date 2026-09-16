#!/usr/bin/env python3
"""Pull the incentive hyperlinks out of a GO-Biz Business Investment Guide PDF.

Why this exists: the guide's table embeds a hyperlink on every incentive name,
and those links are the authoritative "Learn more" destinations. They live in
the PDF's link annotations, NOT in its text layer, so text extraction alone
loses them. This reads the annotations directly.

    pip install pymupdf
    python3 scripts/extract_links.py data/CA-BIG-2026-09.pdf

Writes build/links.json and prints a summary. It does not modify src/data.js —
review the output first, since page ranges shift between editions.
"""
import argparse
import json
import pathlib
import sys

try:
    import pymupdf
except ImportError:
    print("error: pip install pymupdf", file=sys.stderr)
    raise SystemExit(1)

# The incentive-name column sits at the far left of each table page. Contact-page
# links sit in the right-hand column. Both are captured; the x split separates them.
NAME_COLUMN_MAX_X = 200


def extract(pdf_path: pathlib.Path, first_page: int, last_page: int) -> list[dict]:
    doc = pymupdf.open(pdf_path)
    rows: list[dict] = []

    for pno in range(len(doc)):
        page_num = pno + 1
        if not (first_page <= page_num <= last_page):
            continue
        page = doc[pno]
        for link in page.get_links():
            uri = link.get("uri")
            if not uri:
                continue
            rect = pymupdf.Rect(link["from"])
            text = " ".join(page.get_textbox(rect).split())
            rows.append(
                {
                    "page": page_num,
                    "x": round(rect.x0),
                    "y": round(rect.y0),
                    "text": text,
                    "uri": uri,
                    "column": "name" if rect.x0 < NAME_COLUMN_MAX_X else "contact",
                }
            )

    rows.sort(key=lambda r: (r["page"], r["y"], r["x"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=pathlib.Path)
    ap.add_argument("--first-page", type=int, default=6,
                    help="first page of the incentive tables (2026-09 edition: 6)")
    ap.add_argument("--last-page", type=int, default=21,
                    help="last page of the incentive tables (2026-09 edition: 21)")
    ap.add_argument("-o", "--out", type=pathlib.Path,
                    default=pathlib.Path("build/links.json"))
    args = ap.parse_args()

    rows = extract(args.pdf, args.first_page, args.last_page)
    names = [r for r in rows if r["column"] == "name"]
    contacts = [r for r in rows if r["column"] == "contact"]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=1), encoding="utf-8")

    print(f"pages {args.first_page}-{args.last_page}: "
          f"{len(names)} incentive links, {len(contacts)} contact-column links")
    print(f"wrote {args.out}")
    print()
    print("Incentive links in document order (should match src/data.js order):")
    for i, r in enumerate(names):
        print(f"  {i:>2}  {r['text'][:46]:<46}  {r['uri']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
