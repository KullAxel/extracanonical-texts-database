#!/usr/bin/env python3
"""Copy published text assets into docs/ for GitHub Pages.

GitHub Pages is configured to publish only the repository's /docs directory.
The reader cannot fetch ../texts/... from the deployed site, so version files
and segment files that the browser loads must also exist under docs/texts/.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "texts"
DOCS_TEXTS = ROOT / "docs" / "texts"


def copy_tree(src: Path, dst: Path) -> int:
    if not src.exists():
        return 0
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in src.rglob("*"):
        if path.is_file():
            rel = path.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            count += 1
    return count


def main() -> int:
    copied = copy_tree(TEXTS / "versions", DOCS_TEXTS / "versions")
    copied += copy_tree(TEXTS / "segments", DOCS_TEXTS / "segments")
    manifest = TEXTS / "manifest.json"
    if manifest.exists():
        DOCS_TEXTS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest, DOCS_TEXTS / "manifest.json")
        copied += 1
    print(f"synced {copied} docs text assets into {DOCS_TEXTS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
