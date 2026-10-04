# SPDX-License-Identifier: MIT
"""Exercise scripts/render_catalog.py on the synthetic fixture catalog.

The fixture built by fixture_repo.py ships a renderer stub for the validator
tests. These tests copy the real renderer and catalog model over it, so every
generated view is produced by the code that renders the installed bundle.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

TESTS = Path(__file__).resolve().parent
REPOSITORY = TESTS.parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(REPOSITORY / "scripts"))

import catalog_model  # noqa: E402
import fixture_repo  # noqa: E402
import render_catalog  # noqa: E402
import validate  # noqa: E402

TODAY = dt.date(2026, 10, 3)
VIEWS = (
    "references/controls/index.md", "references/controls/S.md", "references/controls/T.md",
    "references/controls/A.md", "references/controls/N.md", "references/controls/D.md",
    "references/mappings.md",
)


class RendererTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = fixture_repo.build(Path(self.temporary.name) / "repo")
        for name in ("render_catalog.py", "catalog_model.py"):
            shutil.copy2(REPOSITORY / "scripts" / name, self.root / "scripts" / name)

    def read(self, relative):
        return (self.root / relative).read_text(encoding="utf-8")

    def write(self, relative, text):
        (self.root / relative).write_text(text, encoding="utf-8")

    def edit_json(self, relative, change):
        data = json.loads(self.read(relative))
        change(data)
        self.write(relative, json.dumps(data, indent=1) + "\n")

    def edit_control(self, cid, change):
        def apply(data):
            change(next(item for item in data["controls"] if item["id"] == cid))
        self.edit_json("catalog/controls.json", apply)

    def set_ledger_status(self, cid, status):
        def apply(data):
            next(entry for entry in data["entries"] if entry["id"] == cid)["status"] = status
        self.edit_json("catalog/ledger.json", apply)

    def render(self, *args):
        """Run the renderer in-process. Return (exit code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = render_catalog.main(["--root", str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def render_ok(self):
        code, out, err = self.render()
        self.assertEqual(code, 0, out + err)


class RenderingTests(RendererTestCase):
    def test_renders_every_view_and_check_passes(self):
        self.render_ok()
        for relative in VIEWS:
            self.assertTrue((self.root / relative).is_file(), relative)
            self.assertTrue(self.read(relative).startswith("<!-- Generated from catalog/controls.json"), relative)
        code, out, _ = self.render("--check")
        self.assertEqual(code, 0, out)
        self.assertIn("Generated catalog views match", out)

    def test_rendering_is_deterministic(self):
        self.render_ok()
        first = {relative: self.read(relative) for relative in VIEWS}
        code, out, _ = self.render()
        self.assertEqual(code, 0)
        self.assertNotIn("wrote ", out)
        self.assertEqual(first, {relative: self.read(relative) for relative in VIEWS})

    def test_rendered_fixture_passes_the_validator_with_the_drift_check(self):
        self.render_ok()
        result = validate.run(self.root, today=TODAY)
        self.assertEqual(result.findings, [])

    def test_index_counts_critical_set_and_cross_cutting_line(self):
        self.render_ok()
        index = self.read("references/controls/index.md")
        self.assertIn("6 controls in 5 pillars.", index)
        self.assertIn("(2 controls)", index)
        self.assertIn("- A: A-01\n", index)
        self.assertIn("- T: T-01\n", index)
        self.assertIn("Cross-cutting (every category): S-01. These controls carry every ASI identifier", index)
        self.assertIn("| Total | 4 | 1 | 1 | 6 | 2 |", index)

    def test_capability_scope_is_marked_on_aiuc_references(self):
        self.render_ok()
        self.assertIn("- AIUC-1: B006.1 (partial; Automation only)", self.read("references/controls/A.md"))
        self.assertIn(f"| [B006.1]({fixture_repo.AIUC_URL}) (Automation only) | A-01 (partial) |",
                      self.read("references/mappings.md"))

    def test_universal_requirements_carry_no_scope_marker(self):
        self.edit_json("catalog/aiuc1-controls.json",
                       lambda data: data["requirements"]["B006"].update(capabilities=["Universal"]))
        self.render_ok()
        self.assertIn("- AIUC-1: B006.1 (partial)\n", self.read("references/controls/A.md"))

    def test_generation_capabilities_are_shortened(self):
        registry = {"requirements": {"C006": {"capabilities": ["Code-generation", "Text-generation",
                                                               "Voice-generation"]}}}
        self.assertEqual(render_catalog.capability_scope("C006.1", registry),
                         "Code-, Text- or Voice-generation only")
        self.assertEqual(render_catalog.capability_scope("C006.1", {}), "")

    def test_cells_and_prose_are_escaped(self):
        self.edit_control("S-01", lambda c: c.update(title="Owner | *scope*"))
        self.set_title_in_ledger("S-01", "Owner | *scope*")
        self.edit_control("S-01", lambda c: c.update(
            statement="The owner MUST review <canary> values and https://example.com/a_b links."))
        self.render_ok()
        index = self.read("references/controls/index.md")
        self.assertIn(r"| Owner \| \*scope\* |", index)
        pillar = self.read("references/controls/S.md")
        self.assertIn("### S-01 Owner | *scope*", pillar)
        self.assertIn("`<canary>`", pillar)
        self.assertIn("`https://example.com/a_b`", pillar)

    def set_title_in_ledger(self, cid, title):
        def apply(data):
            next(entry for entry in data["entries"] if entry["id"] == cid)["title"] = title
        self.edit_json("catalog/ledger.json", apply)

    def test_index_links_use_the_shared_github_slug(self):
        self.assertIs(render_catalog.slugify, catalog_model.slugify)
        self.assertIs(validate.slugify, catalog_model.slugify)
        self.render_ok()
        self.assertIn("[A-01](A.md#a-01-single-dispatch-path)", self.read("references/controls/index.md"))


class LifecycleTests(RendererTestCase):
    def deprecate(self, cid="N-01"):
        self.edit_control(cid, lambda c: c.update(lifecycle="deprecated", deprecated_in="0.2.0", superseded_by="D-01"))
        self.set_ledger_status(cid, "deprecated")

    def withdraw_critical(self, critical_boundary=False):
        self.edit_control("A-01", lambda c: c.update(lifecycle="withdrawn", withdrawn_in="0.2.0",
                                                     superseded_by=["A-02"], critical_boundary=critical_boundary))
        self.set_ledger_status("A-01", "withdrawn")

    def test_deprecated_control_carries_a_lifecycle_line(self):
        self.deprecate()
        self.render_ok()
        pillar = self.read("references/controls/N.md")
        self.assertIn("### N-01 Tamper-evident audit\n\n- **Lifecycle:** deprecated in 0.2.0; superseded by D-01.",
                      pillar)
        index = self.read("references/controls/index.md")
        self.assertIn("Tamper-evident audit (deprecated in 0.2.0; superseded by D-01)", index)
        self.assertIn("6 controls in 5 pillars.", index)

    def test_withdrawn_critical_control_renders_as_a_tombstone(self):
        self.withdraw_critical()
        self.render_ok()
        pillar = self.read("references/controls/A.md")
        self.assertIn("This pillar has 1 control: 1 at Level 2. 1 withdrawn control is kept as a tombstone", pillar)
        tombstones = pillar.split("## Withdrawn", 1)
        self.assertEqual(len(tombstones), 2, pillar)
        self.assertNotIn("### A-01", tombstones[0])
        self.assertIn("### A-01 Single dispatch path\n\n- **Lifecycle:** withdrawn in 0.2.0; superseded by A-02.",
                      tombstones[1])
        self.assertNotIn("**Statement:**", tombstones[1])

    def test_withdrawn_control_leaves_routing_counts_and_mappings(self):
        self.withdraw_critical()
        self.render_ok()
        index = self.read("references/controls/index.md")
        self.assertIn("5 controls in 5 pillars, plus 1 withdrawn control kept as tombstones and not counted.", index)
        self.assertIn("- A: none\n", index)
        self.assertIn("except withdrawn controls (1 controls)", index)
        self.assertNotIn("[A-01]", index)
        self.assertIn("| `tools` | - | A-02 (+external-effect) | N-01 |", index)
        self.assertIn("| Total | 3 | 1 | 1 | 5 | 1 |", index)
        self.assertIn("Withdrawn controls, not counted: A-01.", index)
        self.assertIn("(tombstones in [A.md](A.md#withdrawn)): A-01 (withdrawn in 0.2.0; superseded by A-02).", index)
        mappings = self.read("references/mappings.md")
        self.assertNotIn("A-01 (", mappings)
        self.assertIn("Withdrawn controls are not listed.", mappings)

    def test_renderer_and_validator_agree_on_a_withdrawn_critical_control(self):
        self.withdraw_critical(critical_boundary=False)
        code, out, err = self.render()
        self.assertEqual(code, 0, out + err)
        findings = validate.run(self.root, today=TODAY, run_renderer=False).findings
        self.assertFalse([f for f in findings if f.code == "critical-boundary" and f.path == "catalog/controls.json"],
                         findings)
        self.setUp()
        self.withdraw_critical(critical_boundary=True)
        code, _, err = self.render()
        self.assertEqual(code, 2)
        self.assertIn("A-01: critical_boundary must be false", err)
        findings = validate.run(self.root, today=TODAY, run_renderer=False).findings
        self.assertTrue([f for f in findings if f.code == "critical-boundary" and f.path == "catalog/controls.json"])

    def test_withdrawn_control_needs_a_successor(self):
        self.edit_control("N-01", lambda c: c.update(lifecycle="withdrawn", withdrawn_in="0.2.0"))
        self.set_ledger_status("N-01", "withdrawn")
        code, _, err = self.render()
        self.assertEqual(code, 2)
        self.assertIn("a withdrawn control needs withdrawn_in and superseded_by", err)


class SourceCheckTests(RendererTestCase):
    def assertRenderError(self, text):
        code, _, err = self.render()
        self.assertEqual(code, 2, err)
        self.assertIn(text, err)
        self.assertIn("nothing rendered", err)

    def test_missing_top_level_field(self):
        self.edit_json("catalog/controls.json", lambda data: data.pop("asi_categories"))
        self.assertRenderError("missing top-level field 'asi_categories'")

    def test_critical_boundary_flag_must_follow_the_rule(self):
        self.edit_control("D-01", lambda c: c.update(critical_boundary=True))
        self.assertRenderError("D-01: critical_boundary must be false")

    def test_unknown_applicability_token(self):
        self.edit_control("A-01", lambda c: c.update(applies_when=["toolz"]))
        self.assertRenderError("applies_when token 'toolz' is not in the vocabulary")

    def test_mapping_drift_between_catalog_files(self):
        self.edit_json("catalog/mappings.json",
                       lambda data: data["aiuc1"]["refs"]["A-01"][0].update(relation="supports"))
        self.assertRenderError("aiuc1 refs for A-01 differ from catalog/controls.json")

    def test_ledger_status_must_match_lifecycle(self):
        self.set_ledger_status("N-01", "deprecated")
        self.assertRenderError("N-01 status differs from the catalog lifecycle")

    def test_unknown_successor(self):
        self.edit_control("N-01", lambda c: c.update(lifecycle="deprecated", superseded_by="D-99"))
        self.set_ledger_status("N-01", "deprecated")
        self.assertRenderError("superseded_by names unknown control D-99")

    def test_cited_aiuc_requirement_needs_recorded_capabilities(self):
        self.edit_json("catalog/aiuc1-controls.json", lambda data: data["requirements"].pop("B006"))
        self.assertRenderError("no capabilities recorded for B006")

    def test_unreadable_source_is_a_usage_error(self):
        (self.root / "catalog/aiuc1-controls.json").unlink()
        code, _, err = self.render()
        self.assertEqual(code, 2)
        self.assertIn("cannot read catalog sources", err)


class CheckModeTests(RendererTestCase):
    def test_check_reports_a_stale_view(self):
        self.render_ok()
        self.write("references/controls/A.md", self.read("references/controls/A.md") + "\nHand edit.\n")
        code, out, _ = self.render("--check")
        self.assertEqual(code, 1)
        self.assertIn("references/controls/A.md: out of date", out)

    def test_check_reports_a_missing_view(self):
        self.render_ok()
        (self.root / "references/controls/N.md").unlink()
        code, out, _ = self.render("--check")
        self.assertEqual(code, 1)
        self.assertIn("references/controls/N.md: missing", out)

    def test_check_reports_a_file_the_renderer_does_not_generate(self):
        self.render_ok()
        self.write("references/controls/extra.md", "# Extra\n")
        code, out, _ = self.render("--check")
        self.assertEqual(code, 1)
        self.assertIn("references/controls/extra.md: not generated by the renderer", out)

    def test_check_writes_nothing(self):
        before = self.read("references/controls/A.md")
        code, _, _ = self.render("--check")
        self.assertEqual(code, 1)
        self.assertEqual(self.read("references/controls/A.md"), before)


class SharedModelTests(unittest.TestCase):
    def test_critical_boundary_rule(self):
        rule = catalog_model.is_critical
        self.assertTrue(rule({"level": 1, "failure_severity": "critical"}))
        self.assertTrue(rule({"level": 1, "failure_severity": "critical", "lifecycle": "deprecated"}))
        self.assertFalse(rule({"level": 1, "failure_severity": "critical", "lifecycle": "withdrawn"}))
        self.assertFalse(rule({"level": 2, "failure_severity": "critical"}))
        self.assertFalse(rule({"level": True, "failure_severity": "critical"}))
        self.assertFalse(rule({"level": 1, "failure_severity": "high"}))

    def test_both_scripts_use_the_shared_rule(self):
        self.assertIs(render_catalog.is_critical, catalog_model.is_critical)
        self.assertIs(validate.is_critical, catalog_model.is_critical)
        self.assertIs(validate.PILLARS, catalog_model.PILLARS)

    def test_nist_action_maps_to_its_subcategory(self):
        self.assertEqual(catalog_model.nist_function("GV-1.3-001"), "GOVERN 1.3")
        self.assertEqual(catalog_model.nist_function("MS-2.7-010"), "MEASURE 2.7")
        self.assertIsNone(catalog_model.nist_function("GOVERN 1.3"))


if __name__ == "__main__":
    unittest.main()
