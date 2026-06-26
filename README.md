# Extracanonical Texts Database

A GitHub-ready scholarly starter database of significant Jewish, Christian, Jewish-Christian, Gnostic, Samaritan, Mandaean, and related ancient religious texts/documents that circulated or influenced communities but are outside the later rabbinic Tanakh and/or the traditional 27-book Protestant New Testament canon, with Catholic/Orthodox/Ethiopian variations noted where possible.

Current local version: **v0.3-local**
Generated: 2026-06-25
Entries: **115**

## Files

- `data/texts.yaml` — canonical machine-readable database.
- `data/texts.json` — JSON export.
- `data/texts.csv` — spreadsheet-friendly export.
- `docs/database.md` — human-readable GitHub browsing view.
- `docs/methodology.md` — scope, evidence hierarchy, and uncertainty policy.
- `docs/sources.md` — recurring source anchors and bibliography.
- `docs/index.html` — basic static reader/search interface for GitHub Pages.
- `texts/english/` — one project-hosted English text slot per entry, currently stubs pending rights/source ingestion.
- `texts/manifest.json` — manifest for future text ingestion/search tooling.
- `scripts/ingest_text.py` — rights-aware full-text ingestion pipeline.
- `docs/ingestion.md` — ingestion workflow and source-prep instructions.
- `scripts/validate_database.py` — validation checks.

## Status

This is a living v0.3 catalog, not an exhaustive list. The current pass adds translation-access metadata, one project-hosted English text slot per entry, and a basic reader/search interface. Most best modern translations still need rights/source ingestion before full text can be added.

## Validate

```bash
python3 scripts/validate_database.py
python3 -m unittest discover -s tests -v
```

## Ingest a rights-cleared full text

See `docs/ingestion.md`. Minimal example:

```bash
python3 scripts/ingest_text.py \
  --id AF-001 \
  --source /path/to/rights-cleared-text.txt \
  --translator "Translator Name" \
  --source-edition "Edition / source citation" \
  --rights-status public_domain \
  --license "Public domain" \
  --status available
```

The script updates the project text file, manifest, segment JSONL, canonical JSON/YAML metadata, and reader data copy.

## Publishing note

No license file is included yet. Choose a license before public GitHub publication.


## Reader / study direction

The project now includes a basic static reader at `docs/index.html`. If GitHub Pages is enabled from the `docs/` folder, readers can search/browse the catalog and see the recommended English translation and project text slot for each document.

Future study tools can build on the same structure:

- full-text search across `texts/english/`
- side-by-side source language / English display
- notes and annotations
- cross-reference graph by canonical relationship and related texts
- AI-assisted summarization and comparison over rights-cleared texts
