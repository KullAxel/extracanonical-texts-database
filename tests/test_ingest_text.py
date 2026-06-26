#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "ingest_text.py"


class IngestTextCliTest(unittest.TestCase):
    def make_project(self, root: Path) -> None:
        (root / "data").mkdir(parents=True)
        (root / "docs" / "data").mkdir(parents=True)
        (root / "texts" / "english").mkdir(parents=True)
        (root / "texts" / "segments").mkdir(parents=True)
        obj = {
            "metadata": {"version": "test"},
            "texts": [
                {
                    "id": "AF-001",
                    "title_standard": "1 Clement",
                    "translation_access": {
                        "recommended_english_translation": "Existing recommendation",
                        "translation_literalness": "medium-high",
                        "translation_rights_status": "copyrighted; rights review required before hosting full text",
                        "full_text_hosting_allowed": "rights_review_required",
                        "full_text_url": "",
                        "public_domain_or_open_access_text_url": "",
                        "recommended_print_edition": "Existing edition",
                        "translation_notes": "Existing notes",
                    },
                    "project_text_path": "texts/english/AF-001.md",
                    "project_text_status": "stub_pending_rights_or_source_ingestion",
                }
            ],
        }
        (root / "data" / "texts.json").write_text(json.dumps(obj, indent=2), encoding="utf-8")
        (root / "docs" / "data" / "texts.json").write_text(json.dumps(obj, indent=2), encoding="utf-8")
        (root / "texts" / "manifest.json").write_text(
            json.dumps({"version": "test", "texts": [{"id": "AF-001", "title": "1 Clement", "path": "texts/english/AF-001.md", "status": "stub_pending_rights_or_source_ingestion"}]}, indent=2),
            encoding="utf-8",
        )

    def test_ingests_rights_cleared_text_updates_metadata_manifest_and_segments(self):
        with tempfile.TemporaryDirectory(prefix="ingest-text-test-") as td:
            root = Path(td)
            self.make_project(root)
            source = root / "source.txt"
            source.write_text("Chapter 1\n\nFirst paragraph.\n\nSecond paragraph with more words.", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--id",
                    "AF-001",
                    "--source",
                    str(source),
                    "--translator",
                    "Public Domain Translator",
                    "--source-edition",
                    "Test Public Domain Edition",
                    "--rights-status",
                    "public_domain",
                    "--license",
                    "Public domain",
                    "--status",
                    "available",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("ingested AF-001", result.stdout)

            text_path = root / "texts" / "english" / "AF-001.md"
            text = text_path.read_text(encoding="utf-8")
            self.assertIn("translator: Public Domain Translator", text)
            self.assertIn("source_edition: Test Public Domain Edition", text)
            self.assertIn("rights_status: public_domain", text)
            self.assertIn("First paragraph.", text)

            data = json.loads((root / "data" / "texts.json").read_text(encoding="utf-8"))
            entry = data["texts"][0]
            self.assertEqual(entry["project_text_status"], "available")
            self.assertEqual(entry["translation_access"]["translation_rights_status"], "public_domain")
            self.assertEqual(entry["translation_access"]["full_text_hosting_allowed"], "yes")
            self.assertEqual(entry["translation_access"]["full_text_url"], "texts/english/AF-001.md")
            self.assertIn("Public Domain Translator", entry["translation_access"]["translation_notes"])

            docs_data = json.loads((root / "docs" / "data" / "texts.json").read_text(encoding="utf-8"))
            self.assertEqual(docs_data["texts"][0]["project_text_status"], "available")

            manifest = json.loads((root / "texts" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["texts"][0]["status"], "available")
            self.assertEqual(manifest["texts"][0]["translator"], "Public Domain Translator")

            segments_path = root / "texts" / "segments" / "AF-001.jsonl"
            segments = [json.loads(line) for line in segments_path.read_text(encoding="utf-8").splitlines()]
            self.assertGreaterEqual(len(segments), 2)
            self.assertEqual(segments[0]["id"], "AF-001")
            self.assertIn("First paragraph", "\n".join(seg["text"] for seg in segments))

    def test_refuses_non_cleared_rights_status_without_force(self):
        with tempfile.TemporaryDirectory(prefix="ingest-text-test-") as td:
            root = Path(td)
            self.make_project(root)
            source = root / "source.txt"
            source.write_text("Text", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--id", "AF-001", "--source", str(source), "--rights-status", "copyrighted"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("refusing to ingest", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
