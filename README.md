# California Business Incentives Tool

A filterable browser tool covering all 69 funding programs in the GO-Biz
**California Business Investment Guide** (September 2026).

Filter by category, administering agency, or incentive type; open any program for
the full table row plus a plain-language explanation; shortlist the relevant ones
and export them as a PDF summary. Every "Learn more" link is the guide's own
embedded hyperlink, extracted from the source PDF.

## Quick start

```bash
python3 scripts/build.py          # -> docs/index.html
open docs/index.html              # no server needed
```

## Requirements

Building needs only Python 3. The validation and extraction scripts need a little
more:

```bash
pip install pymupdf               # scripts/extract_links.py
# scripts/check.py also needs node on PATH to evaluate src/data.js
```

## Commands

| Command | What it does |
| --- | --- |
| `python3 scripts/build.py` | Inline `src/data.js` into `src/app.html` → `docs/index.html` |
| `python3 scripts/check.py` | Validate the dataset (fields, duplicates, category counts) |
| `python3 scripts/check.py --pdf data/CA-BIG-2026-09.pdf` | Also verify every link matches the source guide |
| `python3 scripts/extract_links.py data/CA-BIG-2026-09.pdf` | Print/emit the guide's embedded hyperlinks |

## Deploying

`docs/index.html` is fully self-contained. Upload it to any static host —
Netlify, Cloudflare Pages, GitHub Pages — and it works as-is. The build output
lives in `docs/` because GitHub Pages serves only from the repo root or `/docs`. It loads Google
Fonts and jsPDF from CDNs; if jsPDF is unreachable the list export falls back to
a plain-text download.

## Editing

Change `src/data.js` (the programs) or `src/app.html` (markup, styling, behavior),
then rebuild. Never edit `docs/index.html` — it is generated.

See `CLAUDE.md` for architecture notes, known quirks in the source data, and the
procedure for updating to a new edition of the guide.

## Disclaimer

Independent reference built from a published document; not a GO-Biz product.
Program amounts, deadlines and eligibility change frequently — confirm with the
administering agency before relying on anything here.
