"""Exercise failures that would break distribution of the skill package."""

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))
from validate import validate


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "skill"
        shutil.copytree(REPOSITORY, self.root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", ".venv", "artifacts"))

    def codes(self):
        return {finding.code for finding in validate(self.root)}

    def test_current_repository_is_portable(self):
        self.assertEqual(validate(self.root), [])

    def test_missing_bundled_reference_fails(self):
        (self.root / "references/runtime-controls.md").unlink()
        self.assertIn("missing-file", self.codes())
        self.assertIn("missing-link", self.codes())

    def test_link_cannot_escape_checkout(self):
        outside = Path(self.temporary.name) / "private.md"
        outside.write_text("outside package", encoding="utf-8")
        with (self.root / "README.md").open("a", encoding="utf-8") as file:
            file.write("\n[outside](../private.md)\n")
        self.assertIn("link-escape", self.codes())

    def test_symlinked_resource_is_not_bundled_content(self):
        outside = Path(self.temporary.name) / "external.md"
        outside.write_text("external", encoding="utf-8")
        reference = self.root / "references/runtime-controls.md"
        reference.unlink()
        reference.symlink_to(outside)
        self.assertIn("symlink", self.codes())
        self.assertIn("link-escape", self.codes())

    def test_machine_specific_document_path_fails(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as file:
            file.write("\nRead /home/example/private/config.json\n")
        self.assertIn("machine-path", self.codes())

    def test_duplicate_metadata_is_rejected(self):
        path = self.root / "SKILL.md"
        path.write_text(path.read_text().replace("---\n", "---\nname: conflicting-name\n", 1))
        self.assertIn("duplicate-field", self.codes())

    def test_missing_risk_category_is_detected(self):
        path = self.root / "references/owasp-agentic-top-10.md"
        path.write_text(path.read_text().replace("**ASI07:", "**ASI17:"))
        self.assertIn("coverage", self.codes())

    def test_nonportable_file_url_is_rejected(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as file:
            file.write("\n[local](file:///private/notes.md)\n")
        self.assertIn("nonportable-link", self.codes())

    def test_fenced_markdown_example_is_not_a_resource_link(self):
        with (self.root / "README.md").open("a", encoding="utf-8") as file:
            file.write("\n```markdown\n[example](not-a-real-file.md)\n```\n")
        self.assertEqual(validate(self.root), [])


if __name__ == "__main__":
    unittest.main()
