# Methodology

Version: 0.2-local generated 2026-06-25.

This project is a living, source-backed catalog rather than a final canon list. Inclusion is based on one or more of: manuscript preservation, ancient citation, translation history, liturgical or communal use, influence on later Jewish/Christian/Mandaean/Samaritan traditions, or importance within a major discovered corpus such as Qumran or Nag Hammadi.

## Inclusion boundaries

- Focus: roughly Second Temple through late antiquity, with a few later-adjacent corpora included where they preserve or continue earlier trajectories.
- Excluded from “canon” does not mean unimportant or rejected everywhere. Several entries are canonical/deuterocanonical in Catholic, Orthodox, Ethiopian, or other traditions.
- Borderline records are retained where they document a major corpus, major reception history, or disputed case worth tracking.

## Evidence hierarchy

1. Manuscript catalogs and primary witnesses.
2. Critical editions and standard scholarly translations.
3. Academic reference works and peer-reviewed studies.
4. Orientation resources only where clearly marked and not used as final authority.

## Uncertainty handling

Dates use ranges and confidence labels: high, medium-high, medium, low-medium, low. The database separates date evidence, manuscript witnesses, historical use, canonical status, and interpretation to avoid false precision.

## Data model

The canonical source is `data/texts.yaml`; JSON and CSV are derived convenience exports. `scripts/validate_database.py` enforces required fields, unique IDs, controlled categories, and at least one source per entry.
