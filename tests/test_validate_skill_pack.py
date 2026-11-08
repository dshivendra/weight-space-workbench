from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_skill_pack import parse_frontmatter, validate_skill  # noqa: E402


class ValidateSkillTests(unittest.TestCase):
    def test_valid_document_parses_metadata_and_body(self):
        metadata, body = parse_frontmatter(
            '---\nname: sample-skill\ndescription: "Use when the sample task is requested."\n'
            'metadata:\n  version: "1.0"\n---\n\n# Instructions\nDo the task.\n'
        )
        self.assertEqual(metadata["name"], "sample-skill")
        self.assertEqual(metadata["metadata"], {"version": "1.0"})
        self.assertIn("Do the task", body)

    def test_malformed_yaml_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_frontmatter("---\nname: [invalid\n---\nBody")

    def test_directory_name_and_spec_frontmatter_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "sample-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: wrong-name\ndescription: Valid.\ntriggers: x\n---\n\nBody\n",
                encoding="utf-8",
            )
            errors = validate_skill(skill_dir)
            self.assertTrue(any("must match its directory" in error for error in errors))
            self.assertTrue(any("unsupported frontmatter fields" in error for error in errors))

    def test_empty_instruction_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "sample-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Valid.\n---\n",
                encoding="utf-8",
            )
            self.assertTrue(any("body cannot be empty" in error for error in validate_skill(skill_dir)))


if __name__ == "__main__":
    unittest.main()
