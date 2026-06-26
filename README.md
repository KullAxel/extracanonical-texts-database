# Extracanonical Texts Database

A GitHub-ready scholarly starter database of significant Jewish, Christian, Jewish-Christian, Gnostic, Samaritan, Mandaean, and related ancient religious texts/documents that circulated or influenced communities but are outside the later rabbinic Tanakh and/or the traditional 27-book Protestant New Testament canon, with Catholic/Orthodox/Ethiopian variations noted where possible.

Current local version: **v0.2-local**
Generated: 2026-06-25
Entries: **115**

## Files

- `data/texts.yaml` — canonical machine-readable database.
- `data/texts.json` — JSON export.
- `data/texts.csv` — spreadsheet-friendly export.
- `docs/database.md` — human-readable GitHub browsing view.
- `docs/methodology.md` — scope, evidence hierarchy, and uncertainty policy.
- `docs/sources.md` — recurring source anchors and bibliography.
- `scripts/validate_database.py` — validation checks.

## Status

This is a living v0.2 catalog, not an exhaustive list. The first pass normalizes the earlier Markdown draft into a structured schema and expands priority Qumran and Nag Hammadi coverage. More item-level source verification is still needed before making completeness claims.

## Validate

```bash
python3 scripts/validate_database.py
```

## Publishing note

No license file is included yet. Choose a license before public GitHub publication.
