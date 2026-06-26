# Project-hosted English texts

This directory is reserved for English text files used by future search, reader, annotation, and AI study features.

Current status: v0.3 creates one Markdown stub per database entry at `texts/english/<ID>.md` and records the recommended scholarly English translation. Most best modern translations are copyrighted, so the stubs intentionally do not copy full text until rights/public-domain/open-license status is resolved.

For each document, replace the stub with a rights-cleared English text and update:

- `data/texts.yaml`
- `data/texts.json`
- `data/texts.csv`
- `texts/manifest.json`
- `project_text_status`: `available` or `partial`
- `translation_access.full_text_url` if hosted online

Suggested future ingestion metadata per file:

- source edition
- translator
- publication year
- rights/license basis
- source language
- segmentation scheme
- proofread status
