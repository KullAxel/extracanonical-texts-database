#!/usr/bin/env python3
"""Ingest a rights-cleared English text into the project reader corpus.

This script intentionally refuses copyrighted/uncleared sources unless --force is
provided. It updates the project text file, JSON catalog, docs JSON copy,
manifest, and paragraph-level JSONL segments used by future search/AI tooling.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # keep script usable with stdlib only
    yaml = None

CLEARED_RIGHTS = {"public_domain", "open_license", "permission_granted", "project_owner_cleared"}
VALID_STATUS = {"available", "partial"}


def load_catalog(root: Path) -> dict[str, Any]:
    json_path = root / "data" / "texts.json"
    if not json_path.exists():
        raise SystemExit(f"missing catalog: {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))


def save_catalog(root: Path, catalog: dict[str, Any]) -> None:
    text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (root / "data" / "texts.json").write_text(text, encoding="utf-8")
    docs_data = root / "docs" / "data" / "texts.json"
    if docs_data.parent.exists():
        docs_data.write_text(text, encoding="utf-8")
    yaml_path = root / "data" / "texts.yaml"
    if yaml is not None and yaml_path.exists():
        yaml_path.write_text(yaml.safe_dump(catalog, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")


def find_entry(catalog: dict[str, Any], text_id: str) -> dict[str, Any]:
    for entry in catalog.get("texts", []):
        if entry.get("id") == text_id:
            return entry
    raise SystemExit(f"unknown text id: {text_id}")


def yaml_scalar(value: str) -> str:
    # Keep common human-readable values plain in front matter; quote only values
    # that are empty or contain characters likely to confuse simple YAML parsers.
    if value and re.fullmatch(r"[A-Za-z0-9 .,_:;()\-/]+", value):
        return value
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def build_markdown(entry: dict[str, Any], source_text: str, args: argparse.Namespace) -> str:
    title = entry.get("title_standard", args.id)
    ingested_on = _dt.date.today().isoformat()
    body = source_text.strip() + "\n"
    return (
        "---\n"
        f"id: {args.id}\n"
        f"title: {yaml_scalar(title)}\n"
        f"status: {args.status}\n"
        f"translator: {yaml_scalar(args.translator or '')}\n"
        f"source_edition: {yaml_scalar(args.source_edition or '')}\n"
        f"rights_status: {args.rights_status}\n"
        f"license: {yaml_scalar(args.license or '')}\n"
        f"source_file: {yaml_scalar(str(Path(args.source).name))}\n"
        f"ingested_on: {ingested_on}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"Translation/source: {args.source_edition or 'unspecified'}\n\n"
        f"Translator: {args.translator or 'unspecified'}\n\n"
        f"Rights/license basis: {args.rights_status}; {args.license or 'unspecified'}\n\n"
        "## Text\n\n"
        f"{body}"
    )


def segment_text(text_id: str, title: str, markdown: str) -> list[dict[str, Any]]:
    # Strip front matter and top metadata, then split on blank lines. This is a
    # conservative paragraph-level segmentation suitable for first-pass search.
    content = re.sub(r"^---\n.*?\n---\n", "", markdown, flags=re.S)
    content = re.sub(r"^# .+?\n+", "", content, count=1)
    parts = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    segments = []
    for idx, part in enumerate(parts, 1):
        if part.startswith("Translation/source:") or part.startswith("Translator:") or part.startswith("Rights/license basis:") or part == "## Text":
            continue
        segments.append({"id": text_id, "title": title, "segment_index": len(segments) + 1, "text": part})
    return segments


def write_segments(root: Path, text_id: str, segments: list[dict[str, Any]]) -> None:
    seg_dir = root / "texts" / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    path = seg_dir / f"{text_id}.jsonl"
    path.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in segments), encoding="utf-8")


def update_manifest(root: Path, entry: dict[str, Any], args: argparse.Namespace, segments: list[dict[str, Any]]) -> None:
    manifest_path = root / "texts" / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"version": "generated", "texts": []}
    rows = manifest.setdefault("texts", [])
    row = None
    for item in rows:
        if item.get("id") == args.id:
            row = item
            break
    if row is None:
        row = {"id": args.id, "title": entry.get("title_standard", args.id)}
        rows.append(row)
    row.update(
        {
            "title": entry.get("title_standard", args.id),
            "path": entry.get("project_text_path", f"texts/english/{args.id}.md"),
            "status": args.status,
            "translator": args.translator or "",
            "source_edition": args.source_edition or "",
            "rights_status": args.rights_status,
            "license": args.license or "",
            "segment_path": f"texts/segments/{args.id}.jsonl",
            "segment_count": len(segments),
        }
    )
    manifest["updated_on"] = _dt.date.today().isoformat()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ingest(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"source file not found: {source}")
    if args.status not in VALID_STATUS:
        raise SystemExit(f"status must be one of {sorted(VALID_STATUS)}")
    if args.rights_status not in CLEARED_RIGHTS and not args.force:
        raise SystemExit(
            f"refusing to ingest {args.id}: rights-status {args.rights_status!r} is not cleared. "
            "Use public_domain/open_license/permission_granted/project_owner_cleared or pass --force after a rights decision."
        )
    catalog = load_catalog(root)
    entry = find_entry(catalog, args.id)
    source_text = source.read_text(encoding=args.encoding)
    markdown = build_markdown(entry, source_text, args)
    text_path = root / entry.get("project_text_path", f"texts/english/{args.id}.md")
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(markdown, encoding="utf-8")

    tr = entry.setdefault("translation_access", {})
    tr["translation_rights_status"] = args.rights_status
    tr["full_text_hosting_allowed"] = "yes" if args.rights_status in CLEARED_RIGHTS or args.force else "rights_review_required"
    tr["full_text_url"] = entry.get("project_text_path", f"texts/english/{args.id}.md")
    if args.source_url:
        tr["public_domain_or_open_access_text_url"] = args.source_url
    notes = tr.get("translation_notes", "")
    addition = f"Ingested {args.status} project text from {args.source_edition or source.name}; translator: {args.translator or 'unspecified'}; rights basis: {args.rights_status}."
    tr["translation_notes"] = (notes.rstrip() + " " + addition).strip()
    entry["project_text_status"] = args.status

    segments = segment_text(args.id, entry.get("title_standard", args.id), markdown)
    write_segments(root, args.id, segments)
    update_manifest(root, entry, args, segments)
    save_catalog(root, catalog)
    print(f"ingested {args.id}: {text_path.relative_to(root)} ({len(segments)} segments)")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root; defaults to current directory")
    parser.add_argument("--id", required=True, help="Database text ID, e.g. AF-001")
    parser.add_argument("--source", required=True, help="UTF-8 plain-text source file to ingest")
    parser.add_argument("--encoding", default="utf-8", help="Source encoding; default utf-8")
    parser.add_argument("--translator", default="", help="Translator name")
    parser.add_argument("--source-edition", default="", help="Source edition/citation")
    parser.add_argument("--source-url", default="", help="Public/open source URL, if applicable")
    parser.add_argument("--rights-status", required=True, help="public_domain/open_license/permission_granted/project_owner_cleared; other values require --force")
    parser.add_argument("--license", default="", help="License or rights note")
    parser.add_argument("--status", default="available", help="available or partial")
    parser.add_argument("--force", action="store_true", help="Override rights-status refusal after explicit project-owner rights decision")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    return ingest(parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    sys.exit(main())
