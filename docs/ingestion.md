# Full-text ingestion pipeline

This project is now prepared to ingest English full texts for search, reader, annotation, and future AI-study features.

## Current policy

The database records the best scholarly English translation for each document, but full text should only be copied into the repository when one of these is true:

- public domain
- open license
- explicit permission granted
- project owner has made a rights decision and passes `--force`

The ingestion script refuses unclear/copyrighted sources by default.

## Input format

Start with a clean UTF-8 plain-text file. Keep source notes outside the body when possible. The script currently does first-pass paragraph segmentation; later versions can add chapter/verse/section structure.

## Ingest command

Example:

```bash
python3 scripts/ingest_text.py \
  --id AF-001 \
  --source /path/to/1-clement-public-domain.txt \
  --translator "Alexander Roberts and James Donaldson" \
  --source-edition "Ante-Nicene Fathers / Roberts-Donaldson public-domain translation" \
  --source-url "https://ccel.org/ccel/clement_rome/first_epistle_to_the_corinthians/anf01.ii.i.html" \
  --rights-status public_domain \
  --license "Public domain" \
  --status available
```

Accepted rights statuses without `--force`:

- `public_domain`
- `open_license`
- `permission_granted`
- `project_owner_cleared`

For a partial text, use:

```bash
--status partial
```

## Files updated by ingestion

For a document ID such as `AF-001`, the script updates:

- `texts/english/AF-001.md` — project-hosted Markdown text with provenance front matter
- `texts/segments/AF-001.jsonl` — paragraph-level segments for search/AI tooling
- `texts/manifest.json` — text inventory and ingestion metadata
- `data/texts.json` — canonical JSON catalog metadata
- `data/texts.yaml` — canonical YAML catalog, if PyYAML is available locally
- `docs/data/texts.json` — GitHub Pages reader data copy

## Validation

Run:

```bash
python3 scripts/validate_database.py
python3 -m unittest discover -s tests -v
```

The validator now also checks that every project text path exists and that any `available` or `partial` text has a matching segment file.

## Recommended ingestion order

Start with legally simple public-domain/open material, then replace with preferred modern translations only after rights clearance:

1. Apostolic Fathers public-domain fallbacks: 1 Clement, 2 Clement, Didache, Barnabas, Shepherd of Hermas, Ignatius, Polycarp.
2. Public-domain deuterocanonical/apocrypha translations where acceptable as fallback texts.
3. Public-domain older pseudepigrapha translations where they exist, clearly marked as fallback rather than best modern translation.
4. Rights-cleared modern translations for DSS, Nag Hammadi, NT Apocrypha, and other specialized texts.

## Future upgrades

- chapter/section-aware segmentation
- source-language parallel text support
- search index generation
- annotation files per passage
- cross-reference graph from `related_texts` and `relationship_to_canonical_texts`
- AI-ready chunk export with provenance and rights metadata
