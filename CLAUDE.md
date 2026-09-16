# CLAUDE.md

Context for working on this repo. Read before making changes.

## What this is

A single-page, self-contained browser tool for finding California state business
incentives. All 69 programs come from the GO-Biz **California Business Investment
Guide** (September 2026 edition, in `data/`).

The deliverable is **one HTML file with no build dependencies** — `docs/index.html`.
That constraint is deliberate: it has to work opened from disk, emailed as an
attachment, or dropped on any static host. Don't introduce a bundler, a framework,
or a package.json runtime dependency without a clear reason.

## Layout

```
src/app.html        markup, CSS and JS. Contains a /*DATA*/ placeholder.
src/data.js         the 69 incentives as a JS array. Edit this, not dist/.
scripts/build.py    inlines data.js into app.html -> docs/index.html
scripts/extract_links.py   pulls hyperlinks out of a guide PDF
scripts/check.py    validates the dataset; --pdf also verifies link parity
data/               source guide PDFs, one per edition
docs/index.html     generated build output, served by GitHub Pages.
                    Never hand-edit; build.py overwrites it.
```

Build and verify:

```bash
python3 scripts/build.py
python3 scripts/check.py --pdf data/CA-BIG-2026-09.pdf
```

## Things that will bite you

**`docs/index.html` is generated.** Edits there vanish on the next build. Change
`src/app.html` or `src/data.js`.

**Link provenance matters.** Every `url` is the guide's *own* embedded hyperlink,
extracted from the PDF's link annotations — not a URL someone looked up. Several
are non-obvious on purpose: CIIP points at the enabling statute on leginfo, and
the SCE and PG&E rate entries point at PDF fact sheets. Don't "fix" these to
friendlier pages; they'd stop matching the source, and `check.py --pdf` will fail.

**Link annotations are invisible to text extraction.** `pdftotext` and similar
give you the table text but silently drop the hyperlinks. Use
`scripts/extract_links.py` (PyMuPDF), which reads the annotation layer.

**Dataset order is load-bearing.** `src/data.js` is in the same order as the guide's
tables, and `check.py --pdf` pairs the two positionally. Adding or reordering
entries without updating the PDF reference will trip the order-drift check.

**Two fields are transposed in the source.** The Homeless Hiring Tax Credit row
has "$2,500 – $10,000 per hire" under *Total Amount Available* and "$30,000,000
credit annually" under *Maximum Award* — backwards. We reproduce the table as
printed and explain the correct reading in that entry's `detail`. Leave it.

**jsPDF loads from cdnjs.** If it fails to load, export falls back to a `.txt`
download. Keep that fallback working; don't assume `window.jspdf` exists.

**Nine programs have no email.** Their `email` is the literal string
"Contact Page" and they carry a `contactUrl` instead. Any code touching
`email` needs to handle both — see `contactCell()` and `interestMailto()`.

## Conventions

- Vanilla JS, no framework. Keep it that way.
- Colors, type and spacing come from CSS custom properties on `:root`.
- Category colors (`--c-biz`, `--c-emp`, …) encode meaning; they are not decoration.
- Escape anything user- or data-derived with `esc()` before inserting as HTML.
- Prefer `browser storage` only for per-viewer convenience, never for the dataset.

## Updating to a new edition of the guide

1. Drop the new PDF in `data/`.
2. `python3 scripts/extract_links.py data/<new>.pdf` — confirm the page range
   flags (`--first-page` / `--last-page`); tables shift between editions.
3. Diff the printed link list against `src/data.js` and update names, table
   fields and urls for anything that changed.
4. Write `summary` and `detail` for genuinely new programs; keep summaries to
   about two sentences and detail to a short paragraph in plain language.
5. Update `EXPECTED_CATEGORIES` in `scripts/check.py` if counts moved.
6. `python3 scripts/build.py && python3 scripts/check.py --pdf data/<new>.pdf`

## Not official

This is an independent reference built from a published document. It is not a
GO-Biz product. Written summaries are ours, not agency language. Keep the footer
disclaimer accurate if you change scope.
